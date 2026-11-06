"""Unit and inference tests for machine learning predictive models."""

import pytest
from src.ml.predict import prediction_engine
from src.config import FEATURE_COLUMNS


@pytest.fixture
def valid_features():
    return {
        "files_changed": 2,
        "lines_added": 30,
        "lines_deleted": 8,
        "test_count": 35,
        "prev_runtime": 42.0,
        "prev_failure": 0,
        "cpu_usage": 40.0,
        "memory_usage": 280.0,
    }


def test_models_loaded():
    assert prediction_engine.is_loaded is True
    assert prediction_engine.classifier is not None
    assert prediction_engine.regressor is not None
    assert prediction_engine.scaler is not None


def test_prediction_output_structure(valid_features):
    res = prediction_engine.predict(valid_features)
    assert res["valid"] is True
    assert 0.0 <= res["failure_probability"] <= 1.0
    assert res["predicted_failure"] in [0, 1]
    assert 0.0 <= res["model_confidence"] <= 1.0
    assert res["predicted_runtime"] > 0
    assert res["error"] is None


def test_prediction_missing_feature(valid_features):
    invalid = valid_features.copy()
    del invalid["files_changed"]
    res = prediction_engine.predict(invalid)
    assert res["valid"] is False
    assert res["failure_probability"] == 1.0  # Fail-safe high risk
    assert res["model_confidence"] == 0.0     # Fail-safe low confidence
    assert "Missing required feature" in res["error"]


def test_prediction_invalid_feature_type(valid_features):
    invalid = valid_features.copy()
    invalid["cpu_usage"] = "extreme_load"
    res = prediction_engine.predict(invalid)
    assert res["valid"] is False
    assert "must be a numerical value" in res["error"]


def test_prediction_out_of_bounds(valid_features):
    invalid = valid_features.copy()
    invalid["cpu_usage"] = 150.0  # Greater than 100%
    res = prediction_engine.predict(invalid)
    assert res["valid"] is False
    assert "cpu_usage" in res["error"]
