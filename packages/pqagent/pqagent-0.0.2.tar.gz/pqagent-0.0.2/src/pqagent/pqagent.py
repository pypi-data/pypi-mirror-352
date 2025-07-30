from dataclasses import dataclass, field
import copy
import pandas as pd
import ray
import os
import ast
import numpy as np
from typing import Dict, Union
import torch

from dwrappr import save_file, load_file, DataSet
from dwrappr.utils import deep_update

from .preprocessor import Preprocessor

from .sweeper import sweep
from .pqmodel import PqModel
from .mlp import MLP
from .transferlearning import tl_strategies
from .metrics import get_metric
from .mlp import TrainingDataDict

import logging
logger = logging.getLogger(__name__)


@dataclass
class PqAgent:
    preprocessor: Preprocessor = field(init=False)
    models: Dict[str, PqModel] = field(default_factory=dict)

    def __init__(self, config_path: str = None, name: str = "default"):
        # Initialize models as an empty dictionary
        self.models = {}

        self.config = load_file(os.path.join(os.path.dirname(__file__), "./config/base_config.yml"))
        if config_path:
            self.update_config(config_path=config_path)

        # Initialize preprocessor
        self.preprocessor = Preprocessor.from_config(
            config=self.config["preprocessor"]
        )

        self.name = name

    @staticmethod
    def transform_fc_layers_args(config):
        """
        Converts the 'args' in 'fc_layers' from strings to tuples.
        This modifies the config in place if 'fc_layers' is present.
        """
        param_space = config.get('base_model', {}).get('param_space', {})
        if 'fc_layers' in param_space and 'args' in param_space['fc_layers']:
            # Convert the strings to tuples using ast.literal_eval (safer than eval)
            param_space['fc_layers']['args'] = [ast.literal_eval(arg) if isinstance(arg, str) else arg
                                                for arg in param_space['fc_layers']['args']]
        return config

    def update_config(self, config_path:str):
        # If custom config is provided, update the base config
        config = self.config
        updates = load_file(config_path)
        deep_update(config, updates)
        self.config = config

    @classmethod
    def from_file(cls, filepath: str) -> 'PqAgent':
        preprocessor, models = load_file(filepath)
        agent = cls()
        agent.preprocessor = preprocessor
        agent.models = models
        return agent

    @property
    def get_models(self) -> list:
        return list(self.models.keys())

    def train_model(self,
                    data: DataSet,
                    model_name: str = 'base',
                    train_val_split_feature_groups: list = None
                    ) -> None:
        # preprocessing
        transformed_data = self.preprocessor.fit_transform(data)
        train_ds, val_ds = transformed_data.split_dataset(
            first_ds_size=self.config['preprocessor']['train_val_split'],
            shuffle=True,
            group_by_features=train_val_split_feature_groups
        )

        storage_path = f"{os.getcwd()}/agent/"
        train_ds.save(f"{storage_path}/{self.name}_train_ds.joblib")
        val_ds.save(f"{storage_path}/{self.name}_val_ds.joblib")

        # hyperparamter optimization
        best_result, checkpoint = sweep(sweep_config=self.config['train_config']['sweep_config'],
                                        param_space=self.config['train_config']['param_space'],
                                        data=TrainingDataDict(
                                            X_train=train_ds.x_as_tensor,
                                            y_train=train_ds.y_as_tensor,
                                            X_val=val_ds.x_as_tensor,
                                            y_val=val_ds.y_as_tensor
                                        ),
                                        trainable=MLP.train_fn)

        # save base model and metrics of best model from sweep
        tmp_model = PqModel(net=checkpoint['net'])
        tmp_model.set_result(ray_result=best_result)
        self._add_model(model_name=model_name, model=tmp_model)

        logger.info(f"metrics (full dataset): {best_result.metrics}")
        logger.info(f"best model: {best_result.path}")

    def load_model_from_checkpoint(self, model_name: str, trial_id: str = None, checkpoint_path: str = None) -> None:
        if not trial_id or not checkpoint_path:
            raise ValueError(f"Trial id and checkpoint_path are required.")
        if checkpoint_path:
            checkpoint = torch.load(checkpoint_path)
            tmp_model = PqModel(net=checkpoint['net'])
        elif trial_id:
            raise NotImplementedError
            # todo (mid) implement

        self._add_model(model_name=model_name, model=tmp_model)

    def evaluate_model(self,
                       dataset: DataSet,
                       model_to_use: str,
                       ) -> (dict, pd.DataFrame):

        y_pred = self.predict(data=dataset, model_to_use=model_to_use)

        evaluation_metrics = self.eval(y_pred, dataset.y_as_df)
        return evaluation_metrics, y_pred

    def predict(self,
                data: Union[DataSet, pd.DataFrame],
                model_to_use: str
                ) -> pd.DataFrame:

        if isinstance(data, DataSet):
            dataset = data
        elif isinstance(data, pd.DataFrame):
            raise NotImplemented  # todo: funktionalität hinzufügen
        else:
            raise ValueError("datatype of input_data must either be a DataSet or a DataPoint")

        # preprocessing of datasets
        # todo (high): preprocessor transform only works if column order is same in input datasets and the datasets it has been trained on. this leads to very bad predictions without being detected
        dataset = self.preprocessor.transform(dataset)
        X = dataset.x_as_tensor

        # load model to be used
        try:
            model = self._get_model(model_name=model_to_use)
        except:
            raise AttributeError(f"The model {model_to_use} does not exist. Existing models: {self.models.keys()}'")

        y_pred = model.predict(X)
        y_pred = pd.DataFrame(y_pred.detach(), columns=['prediction'])

        return y_pred

    def retrain(self, dataset: DataSet, strategy: str, base_model: str, model_name: str = None) -> None:
        """

        Args:
            base_model: model to retrain based on
            dataset: DataSet to retrain on
            strategy:
                chose from:
                - 'benchmark_model'
                - 'pretrained_model'
                - 'freeze_x_layer_groups'
                - 'fine_tune_model'
                - 'frozen_start_fine_tune_model'

        Returns:

        """

        # todo (high): copy best hyperparameters of base_model for training

        # get network from previously trained model retraining
        if not base_model in self.models.keys():
            raise ValueError(f"base_model {base_model} does not exist")

        if not model_name:
            model_name = strategy.lower()

        net = copy.deepcopy(self.models[base_model].net)

        # Process datasets and set up training
        data = self.preprocessor.transform(dataset)
        train_ds, val_ds = data.split_dataset(
            first_ds_size=self.config['preprocessor']['train_val_split'],
            shuffle=True)

        retrain_sweep_config = self.config['retrain_config']['sweep_config']
        retrain_sweep_config['net'] = net  # Use based_model’s network

        if self.config['retrain_config']['param_space']['copy_from_base_model']:
            retrain_param_space = self.config['train_config']['param_space']
            for param in retrain_param_space:
                arg = self.models[base_model].result.config[param]
                arg = [arg]
                retrain_param_space[param]['args'] = arg
        else:
            retrain_param_space = self.config['retrain_config']['param_space']

        # Check if the strategy is valid
        if strategy not in tl_strategies:
            raise ValueError(f"{strategy} not available in tl-strategies")

        # Perform retraining
        best_result, checkpoint = sweep(
            sweep_config=retrain_sweep_config,
            param_space=retrain_param_space,
            data=TrainingDataDict(
                X_train=train_ds.x_as_tensor,
                y_train=train_ds.y_as_tensor,
                X_val=val_ds.x_as_tensor,
                y_val=val_ds.y_as_tensor
            ),
            trainable=tl_strategies[strategy],
            retrain=True)

        # save base model and metrics of best model from sweep
        tmp_model = PqModel(net=checkpoint['net'])
        tmp_model.set_result(ray_result=best_result)
        self._add_model(model_name=model_name, model=tmp_model)
        logger.info(f"train metrics: {best_result.metrics}")
        logger.info(f"best model: {best_result.path}")

    def compare_models(self):
        # training plots of all strategies into one plot
        pass

    def save(self, file_path: str = None, folder_path: str = None) -> None:
        """
        Save the model and preprocessor to a specified file or folder.

        Parameters:
        - file_path (str, optional): The path to save the file directly.
        - folder_path (str, optional): The folder path to save the file with a default naming convention.

        Raises:
        - ValueError: If neither file_path nor folder_path is provided.
        """
        if file_path:
            # Implement logic to save to the specified file_path
            save_file((self.preprocessor, self.models), file_path)
        elif folder_path:
            # Construct the full file path using os.path.join for better compatibility
            full_path = os.path.join(folder_path, f"{self.name}_agent.joblib")
            save_file((self.preprocessor, self.models), full_path)
        else:
            raise ValueError("Either 'file_path' or 'folder_path' must be specified.")

    def reset_ray(self):
        ray.shutdown()

    def eval(self, y_pred: pd.DataFrame, y_true: pd.DataFrame) -> dict:
        metrics = {
            'mae': get_metric(y_pred, y_true, 'mae'),
            'mse': get_metric(y_pred, y_true, 'mse'),
            'r2': get_metric(y_pred, y_true, 'r2'),
            'rmse': get_metric(y_pred, y_true, 'rmse')
        }
        metrics_normalized = {key: float(value) if isinstance(value, np.float64) else value for key, value in
                              metrics.items()}

        return metrics_normalized

    def _add_model(self, model_name: str, model: PqModel):
        self.models[model_name] = model

    def _get_model(self, model_name: str) -> PqModel:
        return self.models.get(model_name)
