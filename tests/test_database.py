"""Unit tests for SQLite database manager, schema integrity, and persistence."""

from pathlib import Path
import pytest
from src.database.db_manager import DatabaseManager


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_telemetry.db"
    return DatabaseManager(db_path=db_file)


def test_db_initialization(temp_db):
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        tables = [
            row[0]
            for row in cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]
        assert "builds" in tables
        assert "predictions" in tables
        assert "decisions" in tables
        assert "experiments" in tables


def test_record_build_and_history(temp_db):
    b_id = "TEST-BUILD-001"
    row_id = temp_db.record_build(
        build_id=b_id,
        timestamp="2026-11-06T12:00:00Z",
        commit_hash="abc12345",
        branch="main",
        execution_mode="AI_OPTIMIZED",
        execution_strategy="TARGETED_TEST_SUITE",
        status="SUCCESS",
        actual_runtime=14.5,
        test_count=12,
        tests_passed=12,
        tests_failed=0,
        cpu_usage=32.0,
        memory_usage=210.0,
        prediction={"failure_probability": 0.12, "model_confidence": 0.76, "predicted_runtime": 15.0},
        decision={"execution_strategy": "TARGETED_TEST_SUITE", "safety_triggered": False},
        changed_files=["sample_app/inventory.py"],
        selected_tests=["sample_tests/test_inventory.py"],
    )
    assert row_id > 0

    history = temp_db.get_build_history(limit=5)
    assert len(history) == 1
    assert history[0]["build_id"] == b_id
    assert history[0]["actual_runtime"] == 14.5
    assert history[0]["failure_probability"] == 0.12


def test_overview_kpis(temp_db):
    temp_db.record_build(
        build_id="B-1", timestamp="t1", commit_hash="c1", branch="main",
        execution_mode="BASELINE", execution_strategy="FULL_TEST_SUITE",
        status="SUCCESS", actual_runtime=30.0, test_count=30,
        tests_passed=30, tests_failed=0, cpu_usage=40.0, memory_usage=200.0
    )
    temp_db.record_build(
        build_id="B-2", timestamp="t2", commit_hash="c2", branch="main",
        execution_mode="AI_OPTIMIZED", execution_strategy="TARGETED_TEST_SUITE",
        status="SUCCESS", actual_runtime=15.0, test_count=15,
        tests_passed=15, tests_failed=0, cpu_usage=30.0, memory_usage=180.0
    )

    kpis = temp_db.get_overview_kpis()
    assert kpis["total_builds"] == 2
    assert kpis["successful_builds"] == 2
    assert kpis["baseline_avg_runtime_sec"] == 30.0
    assert kpis["optimized_avg_runtime_sec"] == 15.0
    assert kpis["runtime_reduction_pct"] == 50.0
    assert kpis["test_reduction_pct"] == 50.0


def test_record_and_get_experiments(temp_db):
    temp_db.record_experiment(
        experiment_id="EXP-01",
        scenario_name="Test Scenario",
        description="Benchmark scenario",
        baseline_runtime=40.0,
        optimized_runtime=20.0,
        baseline_tests_count=30,
        optimized_tests_count=10,
        baseline_cpu=50.0,
        optimized_cpu=30.0,
        baseline_memory=300.0,
        optimized_memory=200.0,
    )
    exps = temp_db.get_experiments()
    assert len(exps) == 1
    assert exps[0]["scenario_name"] == "Test Scenario"
    assert exps[0]["runtime_savings_pct"] == 50.0
