import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def inverse_log_transform(values):
    return np.expm1(values)


def calculate_metrics(y_true, y_pred, log_target: bool = True) -> dict:
    if log_target:
        y_true = inverse_log_transform(y_true)
        y_pred = inverse_log_transform(y_pred)

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    mape = np.mean(
        np.abs((y_true - y_pred) / y_true)
    ) * 100

    return {
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
    }