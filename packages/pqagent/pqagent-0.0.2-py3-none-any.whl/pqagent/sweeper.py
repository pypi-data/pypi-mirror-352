import os
from datetime import datetime
import uuid
import torch
from ray.air import CheckpointConfig, Result
import ray
from ray import tune
from ray.tune.search.optuna import OptunaSearch
from ray.tune.search.bayesopt import BayesOptSearch
from ray.tune import ResultGrid
from ray import train
import platform

from .mlp import MLP, TrainingDataDict
from dwrappr.utils import df_row_to_nested_dict

import logging
logger = logging.getLogger(__name__)

os.environ["TUNE_WARN_EXCESSIVE_EXPERIMENT_CHECKPOINT_SYNC_THRESHOLD_S"] = "0"


def sweep(data: TrainingDataDict, trainable, sweep_config: dict, param_space: dict, retrain: bool = False) -> (
        dict, MLP):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    exp_name = f"exp_{timestamp}"
    # todo (low): enable for global use
    storage_path = f"{os.getcwd()}/ray/"

    # select path which read/write permissions (windows problem)
    if platform.system() == 'Windows':
        tmp_dir = "/ray_tmp/"
    else:
        tmp_dir = None

    tune_metric = f"{sweep_config['pick_best_model_based_on']}_{sweep_config['metric']}"

    ray.init(_temp_dir=tmp_dir)

    # todo (very low): add custom callback function to define what is logged to tensorboards
    # # Start TensorBoard
    # tb = program.TensorBoard()
    # tb.configure(argv=[None, '--logdir', storage_path])
    # url = tb.launch()
    # webbrowser.open(url)  # Open TensorBoard in the default web browser

    # handle tensorboard not able to show lists
    param_space['fc_layers']['args'] = [str(arg) for arg in param_space['fc_layers']['args']]

    # net hyperparameter optimization
    if not retrain:
        tuner = tune.Tuner(
            trainable=tune.with_parameters(
                trainable=trainable,
                data=data,
                sweep_config=sweep_config,
            ),
            param_space=dict_to_tune(param_space),
            tune_config=tune.TuneConfig(
                num_samples=sweep_config['num_of_sweeps'],  # Number of trials
                metric=tune_metric,
                mode=sweep_config["metric_goal"],
                search_alg=get_search_alg(
                    alg=sweep_config['search_algorithm'],
                    metric=tune_metric,
                    mode=sweep_config["metric_goal"]
                ),
                trial_dirname_creator=trial_dirname_creator
            ),
            run_config=train.RunConfig(
                name=exp_name,
                storage_path=storage_path,
                verbose=sweep_config.get('verbose', 1),
                checkpoint_config=CheckpointConfig(
                    num_to_keep=2,  # don't set to 1 since windows is throwing access errors
                    checkpoint_score_attribute=tune_metric,
                    checkpoint_score_order=sweep_config["metric_goal"]
                ),
            )
        )

    # retraining
    else:
        tuner = tune.Tuner(
            trainable=tune.with_parameters(
                trainable=trainable,
                data=data,
                sweep_config=sweep_config,
            ),
            param_space=dict_to_tune(param_space),
            tune_config=tune.TuneConfig(
                num_samples=1,
                trial_dirname_creator=trial_dirname_creator
            ),
            run_config=train.RunConfig(
                name=exp_name,
                storage_path=storage_path,
                verbose=sweep_config.get('verbose', 1),
                checkpoint_config=CheckpointConfig(
                    num_to_keep=2,  # don't set to 1 since windows is throwing access errors
                    checkpoint_score_attribute=tune_metric,
                    checkpoint_score_order=sweep_config["metric_goal"]
                )
            )
        )

    # Fit the model (run the tuning process)
    results = tuner.fit()
    best_result, checkpoint_of_best_result = get_best_result(
        results=results,
        metric=tune_metric,
        metric_goal=sweep_config['metric_goal']
    )
    ray.shutdown()

    logger.info(
        f"To view sweep results, run the following command in your terminal: tensorboard --logdir {storage_path}{exp_name}")

    return best_result, checkpoint_of_best_result


def get_result_for_best_epoch(result, metric: str, metric_goal: str) -> Result:
    df = result.metrics_dataframe
    if metric_goal == 'max':
        metrics_of_best_epoch = df.loc[df[metric].idxmax()]
    elif metric_goal == 'min':
        metrics_of_best_epoch = df.loc[df[metric].idxmin()]
    else:
        raise ValueError(f"Unknown metric goal: {metric_goal}")
    metrics_of_best_epoch = df_row_to_nested_dict(metrics_of_best_epoch)
    best_result = result
    best_result.metrics = metrics_of_best_epoch
    best_result.checkpoint.path = os.path.join(
        os.path.dirname(best_result.checkpoint.path),
        metrics_of_best_epoch['checkpoint_dir_name']
    )
    return best_result


def get_best_result(results: ResultGrid, metric: str, metric_goal: str) -> tuple[Result, MLP]:
    best_result = None
    for r in results:
        result_for_best_epoch = get_result_for_best_epoch(r, metric, metric_goal)
        if best_result is None:
            best_result = result_for_best_epoch
        elif metric_goal == 'max' and result_for_best_epoch.metrics[metric] > best_result.metrics[metric]:
            best_result = result_for_best_epoch
        elif metric_goal == 'min' and result_for_best_epoch.metrics[metric] < best_result.metrics[metric]:
            best_result = result_for_best_epoch
    with best_result.checkpoint.as_directory() as checkpoint_dir:
        checkpoint = torch.load(os.path.join(checkpoint_dir, "model.pt"), weights_only=False)
    return best_result, checkpoint


def convert_to_tune_distributions(distribution: str, args):
    """
    Converts a distribution name and its arguments to a Tune distribution.

    Args:
        distribution (str): The name of the distribution.
        args: Additional arguments for the distribution.

    Returns:
        tune.distributions.Distribution: The converted Tune distribution.

    Raises:
        KeyError: If the given distribution name is not supported.

    """
    distribution_functions = {
        "uniform": tune.uniform,
        "quniform": tune.quniform,
        "loguniform": tune.loguniform,
        "qloguniform": tune.qloguniform,
        "randn": tune.randn,
        "qrandn": tune.qrandn,
        "randint": tune.randint,
        "qrandint": tune.qrandint,
        "lograndint": tune.lograndint,
        "qlograndint": tune.qlograndint,
        "choice": tune.choice,
        "grid": tune.grid_search
    }
    if distribution in ['choice', 'grid']:
        return distribution_functions[distribution](args)
    else:
        return distribution_functions[distribution](*args)


def dict_to_tune(raytune_config_dict: dict):
    """
    Converts a dictionary of configurations to Ray Tune compatible format.

    Args:
        raytune_config_dict (dict): A dictionary containing configurations.

    Returns:
        dict: A dictionary in Ray Tune compatible format.

    """
    return {key: convert_to_tune_distributions(value["distribution"],
                                               value["args"]) for key, value in
            (raytune_config_dict
             .items())}


def get_search_alg(alg: str, metric: str, mode: str):
    alg = alg.lower()
    available_algorithms = {
        "optunasearch": OptunaSearch(
            metric=metric,
            mode=mode
        ),
        "bayesoptsearch": BayesOptSearch(
            metric=metric,
            mode=mode
        ),
        "dummy": None
    }
    if alg not in available_algorithms:
        raise ValueError(
            f"{alg} has no corresponding functionality. Possible loss functions are: {available_algorithms.keys()}.")
    else:
        return available_algorithms[alg]


def trial_dirname_creator(trial):
    random_name = uuid.uuid4().hex[:8]  # Generate a short UUID
    return f"trial_{random_name}"
