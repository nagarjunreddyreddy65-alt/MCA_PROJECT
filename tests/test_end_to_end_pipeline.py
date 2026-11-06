"""End-to-End integration tests for the full CI/CD optimization pipeline."""

import pytest
from src.runner.pipeline_runner import pipeline_runner
from src.database.db_manager import db_manager


def test_e2e_baseline_pipeline_execution():
    res = pipeline_runner.run_baseline_pipeline(commit_hash="e2e_base_test", branch="test")
    assert res["status"] in ["SUCCESS", "FAILED"]
    assert res["execution_mode"] == "BASELINE"
    assert res["actual_runtime"] > 0
    assert res["test_count"] > 0
    assert len(res["executed_tests"]) == 5

    # Verify persisted in database
    history = db_manager.get_build_history(limit=1)
    assert history[0]["build_id"] == res["build_id"]
    assert history[0]["execution_mode"] == "BASELINE"


def test_e2e_optimized_pipeline_execution():
    res = pipeline_runner.run_optimized_pipeline(
        changed_files=["sample_app/inventory.py"],
        override_features={
            "files_changed": 1,
            "lines_added": 8,
            "lines_deleted": 2,
            "test_count": 30,
            "prev_runtime": 42.0,
            "prev_failure": 0,
            "cpu_usage": 32.0,
            "memory_usage": 220.0,
        },
        commit_hash="e2e_opt_test",
        branch="test",
    )
    assert res["status"] in ["SUCCESS", "FAILED"]
    assert res["execution_mode"] == "AI_OPTIMIZED"
    assert res["actual_runtime"] > 0
    assert res["failure_probability"] is not None
    assert res["model_confidence"] is not None
    assert res["decision_explanation"] is not None

    # Verify persisted in database
    history = db_manager.get_build_history(limit=1)
    assert history[0]["build_id"] == res["build_id"]
    assert history[0]["execution_mode"] == "AI_OPTIMIZED"
