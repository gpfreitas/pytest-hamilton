import pandas as pd


def features(raw_data: pd.DataFrame) -> pd.DataFrame:
    return raw_data[["chas", "nox", "rm"]]


def labels(raw_data: pd.DataFrame) -> pd.Series:
    return raw_data["medv"]


def model_inputs(features: pd.DataFrame, labels: pd.Series) -> dict:
    return {"X": features, "y": labels}
