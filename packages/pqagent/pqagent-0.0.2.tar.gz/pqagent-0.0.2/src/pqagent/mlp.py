import os
from dataclasses import dataclass
import tempfile
import ast
from typing import Union, Tuple


from ray.train import Checkpoint
from ray import train
import torch
from torch import nn

from dwrappr import save_file

import logging
logger = logging.getLogger(__name__)


@dataclass
class TrainingDataDict:
    X_train: torch.Tensor
    y_train: torch.Tensor
    X_val: torch.Tensor
    y_val: torch.Tensor


class MLP(nn.Module):
    def __init__(self,
                 in_features: int,
                 out_features: int,
                 fc_layers: Union[list,str],
                 activation_func: str = None,
                 layer_normalization: bool = False,
                 dropout: float = 0):
        """
        Initializes a multi-layer perceptron (MLP) model.

        Args:
            in_features (int): Number of input features.
            out_features (int): Number of output features.
            fc_layers (list): List of integers for hidden layer sizes.
            activation_func (str): Activation function name ('relu', 'leakyrelu').
            layer_normalization (bool): Whether to use layer normalization.
            dropout (float): Dropout rate.
        """
        super(MLP, self).__init__()

        #transofrm tuple back to list (tuple bc of tensorboard issue see sweep function comment)
        if type(fc_layers) is str:
            fc_layers = ast.literal_eval(fc_layers)
        elif type(fc_layers) is list:
            pass
        else:
            raise ValueError("fc_layers must be a list or list format within string")


        # Validate fc_layers
        if not all(isinstance(x, int) and x >= 0 for x in fc_layers):
            raise ValueError("fc_layers must be a tuple of non-negative integers.")

        self.layer_groups = nn.ModuleDict()
        input_size = in_features

        # Handle the case where there are no hidden layers
        if len(fc_layers) == 1 and fc_layers[0] == 0:
            # Directly add the output layer
            self.layer_groups["layer_group_0"] = nn.Sequential(
                nn.Linear(input_size, out_features)
            )
        else:
            # Create groups of layers automatically
            for i, layer_size in enumerate(fc_layers):
                layers = [nn.Linear(input_size, layer_size)]
                input_size = layer_size  # Update input size for the next layer

                # Optionally add LayerNorm, Activation, and Dropout layers
                if layer_normalization:
                    layers.append(nn.LayerNorm(layer_size))
                if activation_func == "relu":
                    layers.append(nn.ReLU())
                elif activation_func == "leakyrelu":
                    layers.append(nn.LeakyReLU())
                if dropout > 0:
                    layers.append(nn.Dropout(dropout))

                # Create a group name like "layer_group_1", "layer_group_2", etc.
                group_name = f"hidden_layer_{i+1}"
                self.layer_groups[group_name] = nn.Sequential(*layers)

            # Add the final output layer as a group
            group_name = f"output_layer"
            self.layer_groups[group_name] = nn.Sequential(
                nn.Linear(input_size, out_features)
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Defines the computation performed at every call.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Output tensor.
        """
        # Pass through each group sequentially
        for group in self.layer_groups.values():
            x = group(x)
        return x

    @classmethod
    def from_dict(cls, param_space: dict, sweep_config:dict, in_features: int, out_features: int):
        return cls(
            in_features=in_features,
            out_features=out_features,
            fc_layers=param_space.get('fc_layers'),
            activation_func=sweep_config['activation_func'],
            layer_normalization=param_space.get('layer_normalization'),
            dropout=param_space.get('dropout', 0)
        )

    # Training function with checkpointing
    @staticmethod
    def train_fn(param_space: dict, sweep_config: dict, data: TrainingDataDict):

        # Initialize the model with ray_tune param_space choice
        net = MLP.from_dict(
            in_features=data.X_train.shape[1],
            out_features=data.y_train.shape[1],
            sweep_config=sweep_config,
            param_space=param_space)


        base_training_strategy(net=net, param_space=param_space, sweep_config=sweep_config, data=data)

    def freeze_group(self, group_name):
        """Freeze the parameters of a specified group."""
        for param in self.layer_groups[group_name].parameters():
            param.requires_grad = False

    def unfreeze_group(self, group_name):
        """Unfreeze the parameters of a specified group."""
        for param in self.layer_groups[group_name].parameters():
            param.requires_grad = True

    def unfreeze_all(self):
        """Unfreeze all layers in the model."""
        for param in self.parameters():
            param.requires_grad = True

    def reset_layer_weights(self, m):
        """Reset the weights of a given layer."""
        if hasattr(m, 'reset_parameters'):
            m.reset_parameters()

    def reset_layer_group_weights(self, group: str):
        """Reset the weights of specific layer groups."""
        self.layer_groups[group].apply(self.reset_layer_weights)

    def reset_all_weights(self):
        """Reset the weights of all layers in the model."""
        self.apply(self.reset_layer_weights)

    def get_num_of_layer_groups(self):
        """Return the number of layer groups in the model."""
        return len(self.layer_groups)


def base_training_strategy(net: nn.Module,
                           data: TrainingDataDict,
                           param_space:dict,
                           sweep_config: dict,
                           start_epoch: int = 1,
                           epochs:int=None,
                           optimizer = None) -> (nn.Module, torch.optim, any):
    best_train_score = None

    if optimizer is None:
        #rebuild optimizer from param space
        try:
            #paramters from param_space
            optimizer = get_optimizer(optimizer=param_space['optimizer'],
                                      params=[{'params': net.parameters(),
                                               'lr': param_space['learning_rate']}]
                                      )
            save_file(optimizer, './optimizer.joblib')

        except:
            raise AttributeError("some necessary parameters are not defined in sweep_config")

    # general parameters from sweep_config
    loss_fn = get_loss_function(loss_function=sweep_config['loss_function'])

    if epochs is None:
        #get epochs from config
        epochs = sweep_config['epochs']

    # Training loop
    for epoch in range(start_epoch, start_epoch + epochs):
        # set to train mode
        net.train()
        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        train_pred = net(data.X_train)
        train_loss = loss_fn(train_pred, data.y_train)
        train_loss.backward()
        optimizer.step()

        # usage
        net.eval()  # Switch to evaluation mode
        with torch.no_grad():
            val_pred = net(data.X_val)
            val_loss = loss_fn(val_pred, data.y_val)

        metrics = {
            f"train_{sweep_config['metric']}": train_loss.item(),
            f"val_{sweep_config['metric']}": val_loss.item(),
            'epoch': epoch
        }

        best_train_score = report_train_progress(
            metrics, best_train_score, net, optimizer, loss_fn,
            save_checkpoint_based_on=f"{sweep_config['pick_best_model_based_on']}_{sweep_config['metric']}",
            metric_goal=sweep_config['metric_goal']
        )

    return net, optimizer, loss_fn


def report_train_progress(metrics,
                          best_train_score,
                          net, optimizer,
                          loss_fn,
                          save_checkpoint_based_on:str,
                          metric_goal:str):

    # Save checkpoint if we achieve the best accuracy for usage datasets
    # this can be done for val or train dataset based on config.yml
    if check_model_improvement(
            goal=metric_goal,
            new=metrics[save_checkpoint_based_on],
            old=best_train_score
    ):

        best_train_score = metrics[save_checkpoint_based_on]
        with tempfile.TemporaryDirectory() as temp_checkpoint_dir:
            torch.save({
                'net': net,
                'optimizer': optimizer,
                'loss_fn': loss_fn
            }, os.path.join(temp_checkpoint_dir, 'model.pt'))

            checkpoint = Checkpoint.from_directory(temp_checkpoint_dir)
            train.report(
                metrics,
                checkpoint=checkpoint
            )
    else:
        train.report(
            metrics
        )
    return best_train_score


def check_model_improvement(goal, new, old):
    if not old:
        return True
    if goal == 'min':
        if new < old:
            return True
    elif goal == 'max':
        if new > old:
            return True
    else:
        return False


def get_optimizer(optimizer: str, params: list[dict])->torch.optim:
    optimizer = optimizer.lower()
    if optimizer == "sgd":
        optimizer = torch.optim.SGD(params)
    elif optimizer == "adam":
        optimizer = torch.optim.Adam(params)

    else:
        raise ValueError(f"Optimizer {optimizer} not supported")
    return optimizer


def get_loss_function(loss_function: str):
    available_loss_functions = {
        "mae": nn.L1Loss(),
        "mse": nn.MSELoss(),
        "huber": nn.SmoothL1Loss()
    }
    if loss_function not in available_loss_functions:
        raise ValueError(
            f"{loss_function} has no corresponding functionality. Possible loss functions are: {available_loss_functions.keys()}.")
    else:
        return available_loss_functions[loss_function]
