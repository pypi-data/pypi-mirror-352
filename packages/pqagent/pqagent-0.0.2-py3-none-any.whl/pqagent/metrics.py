import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, mean_absolute_error, r2_score, root_mean_squared_error
import numpy as np

def get_metric(prediction, true_values, metric: str):
    # Ensure inputs are either lists, pandas Series, DataFrames, or numpy arrays
    if not isinstance(prediction, (list, pd.Series, pd.DataFrame, np.ndarray)):
        raise TypeError("Prediction must be a list, pandas Series, DataFrame, or numpy array")
    if not isinstance(true_values, (list, pd.Series, pd.DataFrame, np.ndarray)):
        raise TypeError("True values must be a list, pandas Series, DataFrame, or numpy array")

    # Convert DataFrame to Series and handle numpy arrays
    if isinstance(prediction, pd.DataFrame):
        prediction = prediction.squeeze()
    if isinstance(true_values, pd.DataFrame):
        true_values = true_values.squeeze()

    # Convert Series and numpy arrays to list
    if isinstance(prediction, pd.Series) or isinstance(prediction, np.ndarray):
        prediction = prediction.tolist()
    if isinstance(true_values, pd.Series) or isinstance(true_values, np.ndarray):
        true_values = true_values.tolist()

    # Wrap scalars in a list if necessary
    if isinstance(prediction, (int, float, np.float32, np.float64)):
        prediction = [prediction]
    if isinstance(true_values, (int, float, np.float32, np.float64)):
        true_values = [true_values]

    # Calculate the specified metric
    if metric == 'accuracy':
        return accuracy_score(true_values, prediction)
    elif metric == 'precision':
        return precision_score(true_values, prediction, average='weighted')
    elif metric == 'recall':
        return recall_score(true_values, prediction, average='weighted')
    elif metric == 'f1':
        return f1_score(true_values, prediction, average='weighted')
    elif metric == 'mse':
        return mean_squared_error(true_values, prediction)
    elif metric == 'mae':
        return mean_absolute_error(true_values, prediction)
    elif metric == 'r2':
        return r2_score(true_values, prediction)
    elif metric == 'rmse':
        return root_mean_squared_error(true_values, prediction)
    else:
        raise ValueError(f"Unsupported metric: {metric}")

