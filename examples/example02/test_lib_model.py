def test_features_shape(features):
    assert features.shape[1] == 3


def test_labels_are_positive(labels):
    assert (labels > 0).all()


def test_model_inputs_keys(model_inputs):
    assert "X" in model_inputs
    assert "y" in model_inputs


def test_dag_has_features_node(hamilton_fixture_driver):
    names = {n.name for n in hamilton_fixture_driver.list_available_variables()}
    assert "features" in names
