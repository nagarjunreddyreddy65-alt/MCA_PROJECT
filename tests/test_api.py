"""Unit and integration tests for FastAPI endpoint handlers."""

import pytest
from src.api.main import (
    health_check,
    get_overview_kpis,
    predict_pipeline_failure,
    predict_pipeline_runtime,
    analyze_ast_dependencies,
    select_tests_endpoint,
    evaluate_decision_engine,
    get_telemetry_history,
    get_model_metrics,
)
from src.api.schemas import (
    FeatureVectorInput,
    ASTAnalysisRequest,
    TestSelectionRequest,
    DecisionRequest,
)


@pytest.fixture
def sample_feature_input():
    return FeatureVectorInput(
        files_changed=2,
        lines_added=25,
        lines_deleted=5,
        test_count=30,
        prev_runtime=40.0,
        prev_failure=0,
        cpu_usage=35.0,
        memory_usage=250.0,
    )


def test_api_health_check():
    res = health_check()
    assert res["status"] in ["healthy", "degraded"]
    assert res["models_loaded"] is True
    assert res["database_connected"] is True
    assert res["version"] == "1.0.0"


def test_api_overview_kpis():
    res = get_overview_kpis()
    assert "total_builds" in res
    assert "success_rate_pct" in res
    assert "runtime_reduction_pct" in res


def test_api_predict_failure(sample_feature_input):
    res = predict_pipeline_failure(sample_feature_input)
    assert 0.0 <= res.failure_probability <= 1.0
    assert res.predicted_failure in [0, 1]
    assert 0.0 <= res.model_confidence <= 1.0
    assert "Champion" in res.champion_classifier or res.champion_classifier is not None


def test_api_predict_runtime(sample_feature_input):
    res = predict_pipeline_runtime(sample_feature_input)
    assert res.predicted_runtime_sec > 0.0
    assert "Champion" in res.champion_regressor or res.champion_regressor is not None


def test_api_analyze_ast():
    res = analyze_ast_dependencies(ASTAnalysisRequest())
    assert "module_to_tests" in res
    assert "auth" in res["module_to_tests"]


def test_api_select_tests():
    req = TestSelectionRequest(changed_files=["sample_app/inventory.py"])
    res = select_tests_endpoint(req)
    assert "sample_tests/test_inventory.py" in res["selected_tests"]


def test_api_evaluate_decision(sample_feature_input):
    req = DecisionRequest(
        changed_files=["sample_app/inventory.py"],
        features=sample_feature_input,
    )
    res = evaluate_decision_engine(req)
    assert "execution_strategy" in res
    assert "decision_explanation" in res


def test_api_get_telemetry_history():
    res = get_telemetry_history(limit=5)
    assert isinstance(res, list)


def test_api_get_model_metrics():
    res = get_model_metrics()
    assert "classification_benchmarks" in res
    assert "regression_benchmarks" in res
