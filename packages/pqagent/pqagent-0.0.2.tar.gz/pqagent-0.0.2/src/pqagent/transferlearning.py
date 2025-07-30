import torch

from dwrappr import save_file
from .mlp import TrainingDataDict
from .mlp import base_training_strategy


# -------------------------#### Strategies ######-----------------------------------
# strategy_0
def benchmark_model(param_space: dict, sweep_config: dict, data: TrainingDataDict):
    """
    Import model and reset all the weights,
    so that only the model structure is transferred and
    weights are retrained
    """
    net = sweep_config['net']

    # reset the weights of the model
    net.reset_all_weights()

    # Training loop
    base_training_strategy(net=net, data=data, sweep_config=sweep_config, param_space=param_space)


# strategy_2
def pretrained_model(param_space: dict, sweep_config: dict, data: TrainingDataDict):
    """
    Import model and weights;
    training the complete model,
    so that model can be fine-tuned
    using lower learning rate
    """
    net = sweep_config['net']

    # Training loop
    base_training_strategy(net=net, data=data, sweep_config=sweep_config, param_space=param_space)


# strategy_1
def freeze_x_layer_groups(param_space: dict, sweep_config: dict, data: TrainingDataDict):
    """
    Import model and weights;
    Freeze lower x layers of the model,
    so that only upper layers can be fine-tuned
    """
    net = sweep_config['net']
    last_layer_group_to_freeze = sweep_config['strategies']['freeze_x_layer_groups']['last_layer_group_to_freeze']

    # Freezing the lower layers
    for idx, (group_name, group) in enumerate(net.layer_groups.items()):
        net.freeze_group(group_name)
        if last_layer_group_to_freeze == idx:
            break  # exit loop

    # Training loop
    base_training_strategy(net=net, data=data, sweep_config=sweep_config, param_space=param_space)


# strategy_3
def fine_tune_model(param_space: dict, sweep_config: dict, data: TrainingDataDict):
    """
    Import model and weights,
    reset weights of upper layer, starting at "first_layer_to_reset" from config,
    so that they are trained from scratch using higher learning rate;
    weights of lower layers are fine-tuned using lower learning rate
    """

    net = sweep_config['net']
    first_layer_to_reset = sweep_config['strategies']['fine_tune_model']['first_layer_to_reset']

    #tmp
    save_file(net, "/Users/nils/PycharmProjects/dissertation/tl-benchmark/tmp_net.joblib")

    # reset layer_group weights
    group_names = list(net.layer_groups.keys())
    for i in range(first_layer_to_reset, len(group_names)):
        net.reset_layer_group_weights(group_names[i])

    lower_params = []
    upper_params = []

    # Collect parameters for lower and upper layers
    for i, group_name in enumerate(group_names):
        if i <= first_layer_to_reset:
            lower_params += list(net.layer_groups[group_name].parameters())
        else:
            upper_params += list(net.layer_groups[group_name].parameters())

    # Return parameter groups for the optimizer
    param_groups = [
        {'params': lower_params, 'lr': sweep_config['strategies']['fine_tune_model']['lower_layer_learning_rate']},
        {'params': upper_params, 'lr': sweep_config['strategies']['fine_tune_model']['upper_layer_learning_rate']}
    ]
    optimizer = torch.optim.Adam(param_groups)

    # Training loop
    base_training_strategy(
        net=net, data=data,
        sweep_config=sweep_config,
        param_space=param_space,
        optimizer=optimizer
    )


# todo(high) strat 4 debugging
# strategy_4
def frozen_start_fine_tune_model(param_space: dict, sweep_config: dict, data: TrainingDataDict):
    """
    Frozen Start Fine-Tuning Model:
    Import model and weights
    Phase 1: Lower layers frozen, and upper layers trained.
    Phase 2: All layers are trained from endpoint of phase 1, with lower learning rate
    """

    net = sweep_config['net']
    strategy_config = sweep_config['strategies']['frozen_start_fine_tune_model']

    # phase1
    # Freezing the lower layers
    for idx, (group_name, group) in enumerate(net.layer_groups.items()):
        if len(net.layer_groups)-1 == idx:
            #don't freeze last layer (output layer)
            break  # exit loop
        net.freeze_group(group_name)
        if strategy_config['last_layer_group_to_freeze'] == idx:
            break  # exit loop

    # devide training epochs into two phases
    epochs = int(round(sweep_config['epochs'] / 2))

    net, optimizer, loss_fn = base_training_strategy(
        net=net, data=data,
        sweep_config=sweep_config,
        param_space=param_space,
        epochs=epochs,
    )

    # phase2
    # unfreeeze all layers for further training
    net.unfreeze_all()

    # change learning rate of existing optimizer for further training
    for param_group in optimizer.param_groups:
        param_group['lr'] = strategy_config['learning_rate_phase_2']

    base_training_strategy(
        net=net, data=data,
        sweep_config=sweep_config,
        param_space=param_space,
    )


tl_strategies = {
    'benchmark_model': benchmark_model,
    'pretrained_model': pretrained_model,
    'freeze_x_layer_groups': freeze_x_layer_groups,
    'fine_tune_model': fine_tune_model,
    'frozen_start_fine_tune_model': frozen_start_fine_tune_model
}
