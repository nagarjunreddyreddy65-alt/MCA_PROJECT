"""Automated Pipeline Execution Runner & Telemetry Collector.
Executes automated test suites under baseline or AI-optimized modes, collects
hardware telemetry (CPU, RAM, Duration) via psutil, and persists execution records.

Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

import datetime
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional
import psutil

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import BASE_DIR, STRATEGY_FULL_SUITE
from src.analyzer.git_diff import git_analyzer
from src.decision.safety_engine import safety_engine
from src.database.db_manager import db_manager


class PipelineRunner:
    """Executes CI/CD pipelines, tracks resource consumption, and persists telemetry."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or BASE_DIR
        self.tests_dir = "sample_tests"

    def execute_pytest(self, test_paths: List[str]) -> Dict[str, Any]:
        """Runs specified pytest test files and profiles runtime and resource usage."""
        start_time = time.perf_counter()
        proc = psutil.Process()
        initial_mem = proc.memory_info().rss / (1024 * 1024)

        # Build pytest command: run with python -m pytest
        cmd = [sys.executable, "-m", "pytest"] + test_paths + ["-v", "--tb=short"]

        cpu_samples = []
        # Sample CPU load at start
        cpu_samples.append(psutil.cpu_percent(interval=0.05))

        try:
            res = subprocess.run(
                cmd,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            exit_code = res.returncode
            stdout = res.stdout
            stderr = res.stderr
        except Exception as e:
            exit_code = 1
            stdout = ""
            stderr = str(e)

        end_time = time.perf_counter()
        duration = round(end_time - start_time, 3)

        # Sample CPU and memory at end
        cpu_samples.append(psutil.cpu_percent(interval=0.05))
        final_mem = proc.memory_info().rss / (1024 * 1024)
        avg_cpu = round(float(sum(cpu_samples) / max(1, len(cpu_samples))), 2)
        peak_mem = round(max(initial_mem, final_mem), 2)

        # Parse test outcomes from stdout
        passed = 0
        failed = 0
        status = "SUCCESS" if exit_code == 0 else "FAILED"

        for line in stdout.splitlines():
            if " passed" in line or " failed" in line:
                parts = line.split()
                for i, p in enumerate(parts):
                    if "passed" in p and i > 0:
                        try:
                            passed = int(parts[i - 1].replace("=", "").strip())
                        except ValueError:
                            pass
                    if "failed" in p and i > 0:
                        try:
                            failed = int(parts[i - 1].replace("=", "").strip())
                        except ValueError:
                            pass

        return {
            "status": status,
            "exit_code": exit_code,
            "duration": duration,
            "tests_passed": passed,
            "tests_failed": failed,
            "test_count": passed + failed,
            "avg_cpu_percent": avg_cpu,
            "peak_memory_mb": peak_mem,
            "stdout": stdout,
            "stderr": stderr,
        }

    def run_baseline_pipeline(
        self,
        commit_hash: Optional[str] = None,
        branch: str = "main",
    ) -> Dict[str, Any]:
        """Executes Conventional Baseline CI/CD Pipeline (runs complete test suite)."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        build_id = f"BASE-{int(time.time()*1000)}"

        # Full test suite discovery
        all_tests = sorted([
            f.relative_to(self.base_dir).as_posix()
            for f in (self.base_dir / self.tests_dir).glob("**/test_*.py")
        ])

        print(f"[*] Starting Baseline Pipeline [{build_id}] on branch '{branch}'")
        print(f"    Executing Full Test Suite ({len(all_tests)} test files)...")

        exec_res = self.execute_pytest(all_tests)

        # Persist to database
        db_manager.record_build(
            build_id=build_id,
            timestamp=timestamp,
            commit_hash=commit_hash or "HEAD",
            branch=branch,
            execution_mode="BASELINE",
            execution_strategy=STRATEGY_FULL_SUITE,
            status=exec_res["status"],
            actual_runtime=exec_res["duration"],
            test_count=exec_res["test_count"],
            tests_passed=exec_res["tests_passed"],
            tests_failed=exec_res["tests_failed"],
            cpu_usage=exec_res["avg_cpu_percent"],
            memory_usage=exec_res["peak_memory_mb"],
            selected_tests=all_tests,
        )

        return {
            "build_id": build_id,
            "execution_mode": "BASELINE",
            "execution_strategy": STRATEGY_FULL_SUITE,
            "status": exec_res["status"],
            "actual_runtime": exec_res["duration"],
            "test_count": exec_res["test_count"],
            "tests_passed": exec_res["tests_passed"],
            "tests_failed": exec_res["tests_failed"],
            "cpu_usage": exec_res["avg_cpu_percent"],
            "memory_usage": exec_res["peak_memory_mb"],
            "executed_tests": all_tests,
            "timestamp": timestamp,
        }

    def run_optimized_pipeline(
        self,
        changed_files: Optional[List[str]] = None,
        override_features: Optional[Dict[str, Any]] = None,
        commit_hash: Optional[str] = None,
        branch: str = "main",
    ) -> Dict[str, Any]:
        """Executes AI-Optimized CI/CD Pipeline:
        Git Churn -> ML Inference -> AST Test Selection -> Safety Gating -> Execution -> Telemetry
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        build_id = f"OPT-{int(time.time()*1000)}"

        # 1. Identify changed files
        if changed_files is None:
            git_changes = git_analyzer.get_changed_files()
            changed_files = git_changes["all_changed"]
            if not changed_files:
                # Default to sample_app/auth.py if working tree clean
                changed_files = ["sample_app/auth.py"]

        # 2. Extract or formulate feature vector
        if override_features:
            features = override_features
        else:
            git_data = git_analyzer.extract_git_features()
            features = git_data["features"]

        print(f"[*] Starting AI-Optimized Pipeline [{build_id}]")
        print(f"    Modified Files: {changed_files}")

        # 3. Safety-Aware Decision Evaluation
        decision_record = safety_engine.evaluate(
            changed_files=changed_files, features=features
        )

        tests_to_run = decision_record["selected_tests"]
        strategy = decision_record["execution_strategy"]
        print(f"    Decision: {strategy} (Safety Triggered: {decision_record['safety_triggered']})")
        print(f"    Selected Tests: {tests_to_run}")

        # 4. Execute Selected Tests
        exec_res = self.execute_pytest(tests_to_run)

        # 5. Persist complete telemetry record
        prediction_payload = {
            "failure_probability": decision_record["failure_probability"],
            "model_confidence": decision_record["model_confidence"],
            "predicted_runtime": decision_record["predicted_runtime"],
            "predicted_failure": 1 if decision_record["failure_probability"] >= 0.5 else 0,
        }

        db_manager.record_build(
            build_id=build_id,
            timestamp=timestamp,
            commit_hash=commit_hash or "HEAD",
            branch=branch,
            execution_mode="AI_OPTIMIZED",
            execution_strategy=strategy,
            status=exec_res["status"],
            actual_runtime=exec_res["duration"],
            test_count=exec_res["test_count"],
            tests_passed=exec_res["tests_passed"],
            tests_failed=exec_res["tests_failed"],
            cpu_usage=exec_res["avg_cpu_percent"],
            memory_usage=exec_res["peak_memory_mb"],
            prediction=prediction_payload,
            decision=decision_record,
            changed_files=changed_files,
            selected_tests=tests_to_run,
        )

        return {
            "build_id": build_id,
            "execution_mode": "AI_OPTIMIZED",
            "execution_strategy": strategy,
            "status": exec_res["status"],
            "actual_runtime": exec_res["duration"],
            "predicted_runtime": decision_record["predicted_runtime"],
            "failure_probability": decision_record["failure_probability"],
            "model_confidence": decision_record["model_confidence"],
            "safety_triggered": decision_record["safety_triggered"],
            "decision_explanation": decision_record["decision_explanation"],
            "fallback_reason": decision_record["fallback_reason"],
            "test_count": exec_res["test_count"],
            "tests_passed": exec_res["tests_passed"],
            "tests_failed": exec_res["tests_failed"],
            "test_reduction_percentage": decision_record["test_reduction_percentage"],
            "cpu_usage": exec_res["avg_cpu_percent"],
            "memory_usage": exec_res["peak_memory_mb"],
            "executed_tests": tests_to_run,
            "changed_files": changed_files,
            "timestamp": timestamp,
        }


# Global singleton
pipeline_runner = PipelineRunner()
