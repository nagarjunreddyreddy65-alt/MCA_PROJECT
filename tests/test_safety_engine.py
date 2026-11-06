"""Unit tests for safety-aware decision engine rules and fail-safe gating."""

import pytest
from src.decision.safety_engine import safety_engine
from src.config import STRATEGY_FULL_SUITE, STRATEGY_TARGETED


@pytest.fixture
def base_features():
    return {
        "files_changed": 1,
        "lines_added": 10,
        "lines_deleted": 2,
        "test_count": 30,
        "prev_runtime": 40.0,
        "prev_failure": 0,
        "cpu_usage": 30.0,
        "memory_usage": 200.0,
    }


def test_safety_rule_high_risk_forces_full_suite(base_features):
    # Override risk threshold to 0.05 so any failure prob triggers high risk rule
    res = safety_engine.evaluate(
        changed_files=["sample_app/inventory.py"],
        features=base_features,
        override_risk_threshold=0.05,
    )
    assert res["execution_strategy"] == STRATEGY_FULL_SUITE
    assert res["safety_triggered"] is True
    assert "High Risk" in res["decision_explanation"]


def test_safety_rule_low_confidence_forces_full_suite(base_features):
    # Override confidence threshold to 0.99 so confidence is deemed insufficient
    res = safety_engine.evaluate(
        changed_files=["sample_app/inventory.py"],
        features=base_features,
        override_confidence_threshold=0.99,
    )
    assert res["execution_strategy"] == STRATEGY_FULL_SUITE
    assert res["safety_triggered"] is True
    assert "Low Confidence" in res["decision_explanation"]


def test_safety_approves_targeted_when_safe(base_features):
    # Set relaxed thresholds so both low-risk and high-confidence are met
    res = safety_engine.evaluate(
        changed_files=["sample_app/inventory.py"],
        features=base_features,
        override_risk_threshold=0.95,
        override_confidence_threshold=0.10,
    )
    assert res["execution_strategy"] == STRATEGY_TARGETED
    assert res["safety_triggered"] is False
    assert "TARGETED TEST EXECUTION APPROVED" in res["decision_explanation"]
    assert res["test_reduction_percentage"] > 0.0


def test_safety_fallback_on_missing_features():
    res = safety_engine.evaluate(
        changed_files=["sample_app/inventory.py"],
        features=None,
    )
    assert res["execution_strategy"] == STRATEGY_FULL_SUITE
    assert res["safety_triggered"] is True
    assert "Missing input telemetry" in res["decision_explanation"]


def test_safety_fallback_on_non_python_change(base_features):
    res = safety_engine.evaluate(
        changed_files=["config.yaml"],
        features=base_features,
    )
    assert res["execution_strategy"] == STRATEGY_FULL_SUITE
    assert res["safety_triggered"] is True
    assert "AST Fallback" in res["decision_explanation"]
