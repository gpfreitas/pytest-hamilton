import pandas as pd
import pytest


@pytest.fixture
def input_config():
    """Supply a small in-memory DataFrame as the Hamilton DAG input.

    The quickstart module expects a 'raw_data' DataFrame with columns
    chas, nox, rm, medv.  JSON cannot encode DataFrames, so we override
    the plugin's default input_config fixture here instead of using
    --hamilton-config.
    """
    df = pd.DataFrame(
        {
            "chas": [0, 1, 0],
            "nox": [0.5, 0.6, 0.7],
            "rm": [6.0, 6.5, 7.0],
            "medv": [20.0, 25.0, 30.0],
        }
    )
    return {"raw_data": df}
