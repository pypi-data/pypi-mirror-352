from dataclasses import dataclass, field

import pandas as pd
from absl.testing.parameterized import parameters
from matplotlib import pyplot as plt
import torch
from ray.air import Result

from dwrappr import save_file, load_file

import logging
logger = logging.getLogger(__name__)

@dataclass
class PqModel():
    net: torch.nn.Module = field(init=True)
    result: Result = field(default_factory=dict, init=False)

    @classmethod
    def load_model(cls, filepath: str):
        model = load_file(filepath)
        return model

    @property
    def metrics(self):
        return self.result.metrics

    def set_result(self, ray_result: Result):
        self.result = ray_result

    def predict(self, X: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        self.net.eval()
        return self.net(X)

    def save(self, path: str, *args, **kwargs) -> None:
        save_file(self, path)

    def get_training_graph(self, metrics=list, show_plot:bool=True)->plt.figure:
        for metric in metrics:
            if metric not in self.result.metrics_dataframe.columns:
                raise ValueError(f"Entry '{metric}' not found in metrics of model.")
        for metric in metrics:
            plt.plot(self.result.metrics_dataframe['epoch'], self.result.metrics_dataframe[metric], label=metric)
        plt.xlabel("epoch")
        plt.legend()
        if show_plot:
            plt.show()
        return plt

    def get_parameters(self):
        for name, param in self.net.named_parameters():
            if 'weight' in name:
                print(f"Layer: {name} | Weights: {param.data}")
            elif 'bias' in name:
                print(f"Layer: {name} | Biases: {param.data}")


