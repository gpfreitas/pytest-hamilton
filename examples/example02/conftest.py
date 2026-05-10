import polars as pl
import pytest


@pytest.fixture
def input_config():
    """Supply a small in-memory DataFrame as the Hamilton DAG input.

    The pipeline's root input (`raw_data`) is a polars DataFrame, which
    cannot be expressed in JSON. Overriding `input_config` in conftest.py
    is the recommended approach for any input that isn't a JSON primitive.
    """
    df = pl.DataFrame(
        {
            "chas": [0, 1, 0],
            "nox": [0.5, 0.6, 0.7],
            "rm": [6.0, 6.5, 7.0],
            "medv": [20.0, 25.0, 30.0],
        }
    )
    return {"raw_data": df}
