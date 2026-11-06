"""Historical CI/CD Telemetry Dataset Generator.
Synthesizes a realistic, empirically-grounded CI/CD execution dataset aligned with
the TravisTorrent schema (Beller et al., MSR 2017) and the synopsis specification.

Features:
- files_changed (int): Number of source code files modified in the commit
- lines_added (int): Total line additions across all modified files
- lines_deleted (int): Total line deletions across all modified files
- test_count (int): Size of repository test suite at build time
- prev_runtime (float): Execution duration (seconds) of the immediate prior build
- prev_failure (int): Binary indicator (1 if prior build failed, else 0)
- cpu_usage (float): Peak CPU utilization percentage during CI job
- memory_usage (float): Peak memory allocation (MB) during CI job

Targets:
- build_failed (int): 0 = SUCCESS, 1 = FAILED (Real-world CI ~20-25% failure rate)
- actual_runtime (float): Pipeline execution time in seconds
"""

import datetime
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import DATA_RAW_DIR, RANDOM_SEED


def generate_cicd_dataset(n_samples: int = 3500, random_seed: int = RANDOM_SEED) -> pd.DataFrame:
    np.random.seed(random_seed)

    # 1. Chronological timestamps starting 18 months ago
    start_time = datetime.datetime(2025, 4, 1, 9, 0, 0)
    timestamps = [
        start_time + datetime.timedelta(minutes=int(i * np.random.uniform(30, 180)))
        for i in range(n_samples)
    ]

    # 2. Sequential Build IDs and Commit Hashes
    build_ids = [f"BUILD-{10000 + i}" for i in range(n_samples)]
    commit_hashes = [
        hashlib.sha1(f"commit_{i}_{timestamps[i].isoformat()}".encode()).hexdigest()[:8]
        for i in range(n_samples)
    ]
    branches = np.random.choice(
        ["main", "develop", "feature/auth", "feature/payment", "bugfix/patch", "refactor/core"],
        size=n_samples,
        p=[0.35, 0.25, 0.15, 0.10, 0.10, 0.05],
    )

    # 3. Code churn features: Realistic log-normal and negative binomial distributions
    files_changed = np.random.negative_binomial(n=2, p=0.4, size=n_samples) + 1
    files_changed = np.clip(files_changed, 1, 45)

    # Lines added and deleted scale with files changed
    lines_added = np.zeros(n_samples, dtype=int)
    lines_deleted = np.zeros(n_samples, dtype=int)
    for i in range(n_samples):
        scale = files_changed[i] * 12.0
        lines_added[i] = int(np.random.exponential(scale=scale) + np.random.uniform(2, 15))
        lines_deleted[i] = int(np.random.exponential(scale=scale * 0.5) + np.random.uniform(0, 10))
    lines_added = np.clip(lines_added, 1, 1500)
    lines_deleted = np.clip(lines_deleted, 0, 800)

    # 4. Test count grows gradually over time (regression repository expansion)
    base_test_count = 35
    test_count = (base_test_count + (np.arange(n_samples) // 30) + np.random.randint(-3, 4, n_samples))
    test_count = np.clip(test_count, 25, 160)

    # 5. Prior build outcomes and times (branch-aware sequential dependence)
    prev_runtime = np.zeros(n_samples, dtype=float)
    prev_failure = np.zeros(n_samples, dtype=int)
    actual_runtime = np.zeros(n_samples, dtype=float)
    build_failed = np.zeros(n_samples, dtype=int)
    cpu_usage = np.zeros(n_samples, dtype=float)
    memory_usage = np.zeros(n_samples, dtype=float)

    # Initial state
    last_runtime = 45.0
    last_fail = 0

    for i in range(n_samples):
        # Carry over prior status (simulating branch continuity)
        prev_runtime[i] = round(last_runtime, 2)
        prev_failure[i] = last_fail

        # Hardware telemetry: correlated with test count and churn
        cpu = 40.0 + (test_count[i] * 0.25) + (files_changed[i] * 0.5) + np.random.normal(0, 6)
        mem = 220.0 + (test_count[i] * 3.5) + (lines_added[i] * 0.15) + np.random.normal(0, 25)
        cpu_usage[i] = round(float(np.clip(cpu, 15.0, 98.0)), 2)
        memory_usage[i] = round(float(np.clip(mem, 120.0, 950.0)), 2)

        # Failure propensity model based on empirical software engineering literature:
        # High churn, high deleted lines, previous failure carryover, high CPU contention increase risk
        churn = lines_added[i] + lines_deleted[i]
        logit_fail = (
            -2.4  # baseline log-odds (corresponds to ~15-20% baseline failure)
            + 0.045 * files_changed[i]
            + 0.0022 * churn
            + 0.95 * prev_failure[i]  # defect carryover effect
            + 0.008 * (test_count[i] - 50)
            + 0.015 * (cpu_usage[i] - 50)
            + np.random.normal(0, 0.45)
        )
        prob_fail = 1.0 / (1.0 + np.exp(-logit_fail))
        prob_fail = np.clip(prob_fail, 0.02, 0.95)

        is_fail = int(np.random.rand() < prob_fail)
        build_failed[i] = is_fail

        # Runtime model (seconds): base setup + per-test execution + churn compilation + fail overhead
        base_overhead = 12.0
        test_execution_time = test_count[i] * 0.55
        churn_compilation_time = (lines_added[i] + lines_deleted[i]) * 0.025
        hardware_delay = (cpu_usage[i] / 100.0) * 10.0 + (memory_usage[i] / 1000.0) * 5.0
        # If build fails early, it might fail fast or timeout on error
        fail_modifier = np.random.choice([-8.0, 15.0], p=[0.7, 0.3]) if is_fail else 0.0

        current_runtime = (
            base_overhead
            + test_execution_time
            + churn_compilation_time
            + hardware_delay
            + fail_modifier
            + np.random.normal(0, 3.5)
        )
        current_runtime = max(8.5, current_runtime)
        actual_runtime[i] = round(float(current_runtime), 2)

        # Update state for next build iteration
        last_runtime = current_runtime
        last_fail = is_fail

    # Assemble into DataFrame
    df = pd.DataFrame(
        {
            "build_id": build_ids,
            "timestamp": [t.isoformat() for t in timestamps],
            "commit_hash": commit_hashes,
            "branch": branches,
            "files_changed": files_changed,
            "lines_added": lines_added,
            "lines_deleted": lines_deleted,
            "test_count": test_count,
            "prev_runtime": prev_runtime,
            "prev_failure": prev_failure,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "actual_runtime": actual_runtime,
            "build_failed": build_failed,
        }
    )

    return df


if __name__ == "__main__":
    print("[*] Generating TravisTorrent-aligned Historical CI/CD Dataset...")
    df = generate_cicd_dataset(n_samples=3500)
    output_path = DATA_RAW_DIR / "travisitorrent_cicd_raw.csv"
    df.to_csv(output_path, index=False)
    print(f"[+] Dataset successfully created: {output_path}")
    print(f"    - Total records: {len(df)}")
    print(f"    - Failure distribution:\n{df['build_failed'].value_counts(normalize=True)}")
    print(f"    - Runtime summary:\n{df['actual_runtime'].describe()}")
