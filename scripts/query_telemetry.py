"""Command-line utility to inspect SQLite CI/CD telemetry and benchmark records.
Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

from pathlib import Path
import sqlite3
import sys

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import DATABASE_PATH


def query_telemetry():
    if not DATABASE_PATH.exists():
        print(f"[!] Database file not found at: {DATABASE_PATH}")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("AI-DRIVEN CI/CD PIPELINE TELEMETRY SUMMARY")
    print("=" * 70)

    # Total counts
    total_builds = cursor.execute("SELECT COUNT(*) FROM builds").fetchone()[0]
    total_exps = cursor.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
    print(f"Total Pipeline Builds Logged : {total_builds}")
    print(f"Empirical Benchmark Scenarios: {total_exps}\n")

    print(f"{'Build ID':<22} | {'Mode':<14} | {'Strategy':<20} | {'Status':<8} | {'Runtime':<8} | {'Tests'}")
    print("-" * 88)

    rows = cursor.execute(
        "SELECT build_id, execution_mode, execution_strategy, status, actual_runtime, test_count FROM builds ORDER BY id DESC LIMIT 10"
    ).fetchall()

    for r in rows:
        print(f"{r['build_id']:<22} | {r['execution_mode']:<14} | {r['execution_strategy']:<20} | {r['status']:<8} | {r['actual_runtime']:<8.2f} | {r['test_count']}")

    print("\n" + "=" * 70)
    print("EMPIRICAL BENCHMARKS (Baseline vs. AI-Optimized)")
    print("=" * 70)
    print(f"{'Scenario ID':<10} | {'Scenario Name':<28} | {'Base Time':<10} | {'Opt Time':<10} | {'Savings %'}")
    print("-" * 75)

    exp_rows = cursor.execute(
        "SELECT experiment_id, scenario_name, baseline_runtime, optimized_runtime, runtime_savings_pct FROM experiments ORDER BY id ASC"
    ).fetchall()

    for e in exp_rows:
        print(f"{e['experiment_id']:<10} | {e['scenario_name']:<28} | {e['baseline_runtime']:<10.2f} | {e['optimized_runtime']:<10.2f} | {e['runtime_savings_pct']:<8.1f}%")

    conn.close()


if __name__ == "__main__":
    query_telemetry()
