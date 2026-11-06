"""SQLite Telemetry Database Manager.
Manages persistent storage for CI/CD builds, ML predictions, safety decisions,
executed test suites, and empirical benchmark experiments.

Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

from pathlib import Path
import sqlite3
import sys
from typing import Any, Dict, List, Optional

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import DATABASE_PATH


class DatabaseManager:
    """Provides high-level persistent CRUD operations for CI/CD telemetry."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DATABASE_PATH
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes tables if they do not exist."""
        schema_path = Path(__file__).parent / "schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found at {schema_path}")
        schema_sql = schema_path.read_text(encoding="utf-8")

        with self.get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    def record_build(
        self,
        build_id: str,
        timestamp: str,
        commit_hash: str,
        branch: str,
        execution_mode: str,
        execution_strategy: str,
        status: str,
        actual_runtime: float,
        test_count: int,
        tests_passed: int,
        tests_failed: int,
        cpu_usage: float,
        memory_usage: float,
        prediction: Optional[Dict[str, Any]] = None,
        decision: Optional[Dict[str, Any]] = None,
        changed_files: Optional[List[str]] = None,
        selected_tests: Optional[List[str]] = None,
    ) -> int:
        """Atomically inserts build telemetry, predictions, and decisions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO builds (
                    build_id, timestamp, commit_hash, branch,
                    execution_mode, execution_strategy, status,
                    actual_runtime, test_count, tests_passed, tests_failed,
                    cpu_usage, memory_usage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    build_id,
                    timestamp,
                    commit_hash,
                    branch,
                    execution_mode,
                    execution_strategy,
                    status,
                    actual_runtime,
                    test_count,
                    tests_passed,
                    tests_failed,
                    cpu_usage,
                    memory_usage,
                ),
            )
            row_id = cursor.lastrowid

            # Insert prediction record
            if prediction:
                cursor.execute(
                    """
                    INSERT INTO predictions (
                        build_id, failure_probability, model_confidence,
                        predicted_runtime, predicted_failure,
                        champion_classifier, champion_regressor
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        build_id,
                        prediction.get("failure_probability", 0.0),
                        prediction.get("model_confidence", 0.0),
                        prediction.get("predicted_runtime", 0.0),
                        prediction.get("predicted_failure", 0),
                        prediction.get("champion_classifier", "Random Forest"),
                        prediction.get("champion_regressor", "Linear Regression"),
                    ),
                )

            # Insert decision record
            if decision:
                cursor.execute(
                    """
                    INSERT INTO decisions (
                        build_id, execution_strategy, safety_triggered,
                        fallback_reason, decision_explanation,
                        risk_threshold, confidence_threshold
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        build_id,
                        decision.get("execution_strategy", "FULL_TEST_SUITE"),
                        1 if decision.get("safety_triggered") else 0,
                        decision.get("fallback_reason"),
                        decision.get("decision_explanation", ""),
                        decision.get("risk_threshold", 0.70),
                        decision.get("confidence_threshold", 0.65),
                    ),
                )

            # Insert changed files
            if changed_files:
                for f in changed_files:
                    cursor.execute(
                        "INSERT INTO build_files (build_id, file_path, change_type) VALUES (?, ?, ?)",
                        (build_id, f, "MODIFIED"),
                    )

            # Insert executed tests
            if selected_tests:
                for t in selected_tests:
                    cursor.execute(
                        "INSERT INTO build_tests (build_id, test_path, status) VALUES (?, ?, ?)",
                        (build_id, t, "PASSED" if status == "SUCCESS" else "FAILED"),
                    )

            conn.commit()
            return row_id

    def get_build_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves chronological execution build history with predictions."""
        query = """
        SELECT 
            b.build_id, b.timestamp, b.commit_hash, b.branch,
            b.execution_mode, b.execution_strategy, b.status,
            b.actual_runtime, b.test_count, b.tests_passed, b.tests_failed,
            b.cpu_usage, b.memory_usage,
            p.failure_probability, p.model_confidence, p.predicted_runtime,
            d.safety_triggered, d.fallback_reason, d.decision_explanation
        FROM builds b
        LEFT JOIN predictions p ON b.build_id = p.build_id
        LEFT JOIN decisions d ON b.build_id = d.build_id
        ORDER BY b.id DESC
        LIMIT ?
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(query, (limit,)).fetchall()
            return [dict(row) for row in rows]

    def get_overview_kpis(self) -> Dict[str, Any]:
        """Calculates global dashboard KPIs comparing baseline and AI-optimized pipelines."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Total counts
            total_builds = cursor.execute("SELECT COUNT(*) FROM builds").fetchone()[0]
            success_builds = cursor.execute("SELECT COUNT(*) FROM builds WHERE status = 'SUCCESS'").fetchone()[0]
            failed_builds = cursor.execute("SELECT COUNT(*) FROM builds WHERE status = 'FAILED'").fetchone()[0]

            # Mode averages
            base_stats = cursor.execute(
                """
                SELECT AVG(actual_runtime), AVG(test_count), AVG(cpu_usage), AVG(memory_usage)
                FROM builds WHERE execution_mode = 'BASELINE'
                """
            ).fetchone()

            opt_stats = cursor.execute(
                """
                SELECT AVG(actual_runtime), AVG(test_count), AVG(cpu_usage), AVG(memory_usage)
                FROM builds WHERE execution_mode = 'AI_OPTIMIZED'
                """
            ).fetchone()

            base_runtime = base_stats[0] or 0.0
            opt_runtime = opt_stats[0] or 0.0
            base_tests = base_stats[1] or 0.0
            opt_tests = opt_stats[1] or 0.0

            runtime_reduction_pct = (
                round(((base_runtime - opt_runtime) / base_runtime) * 100.0, 2)
                if base_runtime > 0 and opt_runtime > 0
                else 0.0
            )

            test_reduction_pct = (
                round(((base_tests - opt_tests) / base_tests) * 100.0, 2)
                if base_tests > 0 and opt_tests > 0
                else 0.0
            )

            return {
                "total_builds": total_builds,
                "successful_builds": success_builds,
                "failed_builds": failed_builds,
                "success_rate_pct": round((success_builds / max(1, total_builds)) * 100.0, 2),
                "baseline_avg_runtime_sec": round(base_runtime, 2),
                "optimized_avg_runtime_sec": round(opt_runtime, 2),
                "runtime_reduction_pct": runtime_reduction_pct,
                "baseline_avg_tests": round(base_tests, 1),
                "optimized_avg_tests": round(opt_tests, 1),
                "test_reduction_pct": test_reduction_pct,
                "baseline_avg_cpu": round(base_stats[2] or 0.0, 2),
                "optimized_avg_cpu": round(opt_stats[2] or 0.0, 2),
                "baseline_avg_mem": round(base_stats[3] or 0.0, 2),
                "optimized_avg_mem": round(opt_stats[3] or 0.0, 2),
            }

    def record_experiment(
        self,
        experiment_id: str,
        scenario_name: str,
        description: str,
        baseline_runtime: float,
        optimized_runtime: float,
        baseline_tests_count: int,
        optimized_tests_count: int,
        baseline_cpu: float,
        optimized_cpu: float,
        baseline_memory: float,
        optimized_memory: float,
        defect_injected: int = 0,
        baseline_defect_detected: int = 0,
        optimized_defect_detected: int = 0,
    ):
        """Records a controlled empirical experiment comparison."""
        runtime_savings = (
            round(((baseline_runtime - optimized_runtime) / baseline_runtime) * 100.0, 2)
            if baseline_runtime > 0
            else 0.0
        )
        test_reduction = (
            round(((baseline_tests_count - optimized_tests_count) / baseline_tests_count) * 100.0, 2)
            if baseline_tests_count > 0
            else 0.0
        )

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO experiments (
                    experiment_id, scenario_name, description,
                    baseline_runtime, optimized_runtime, runtime_savings_pct,
                    baseline_tests_count, optimized_tests_count, test_reduction_pct,
                    baseline_cpu, optimized_cpu, baseline_memory, optimized_memory,
                    defect_injected, baseline_defect_detected, optimized_defect_detected
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experiment_id,
                    scenario_name,
                    description,
                    baseline_runtime,
                    optimized_runtime,
                    runtime_savings,
                    baseline_tests_count,
                    optimized_tests_count,
                    test_reduction,
                    baseline_cpu,
                    optimized_cpu,
                    baseline_memory,
                    optimized_memory,
                    defect_injected,
                    baseline_defect_detected,
                    optimized_defect_detected,
                ),
            )
            conn.commit()

    def get_experiments(self) -> List[Dict[str, Any]]:
        """Retrieves all experimental evaluation records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("SELECT * FROM experiments ORDER BY id ASC").fetchall()
            return [dict(row) for row in rows]


# Global singleton
db_manager = DatabaseManager()
