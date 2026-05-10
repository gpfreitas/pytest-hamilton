import polars as pl


def features(raw_data: pl.DataFrame) -> pl.DataFrame:
    return raw_data.select(["chas", "nox", "rm"])


def labels(raw_data: pl.DataFrame) -> pl.Series:
    return raw_data["medv"]


def model_inputs(features: pl.DataFrame, labels: pl.Series) -> dict:
    return {"X": features, "y": labels}
