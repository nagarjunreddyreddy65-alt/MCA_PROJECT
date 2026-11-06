# DATASET DOCUMENTATION: CI/CD HISTORICAL TELEMETRY

**Project:** AI-Driven CI/CD Pipeline Optimization  
**MCA Major Project:** Dayananda Sagar College of Engineering, Bangalore  
**Author:** NAGARJUNREDDY (1DS25MC052)  
**Supervisor:** Prof. Mahendra Kumar B  

---

## 1. Overview & Lineage

The dataset represents continuous integration and continuous deployment pipeline executions modeled after the empirical distribution of the **TravisTorrent** research corpus (Beller et al., MSR 2017) and live CI/CD system telemetry.

The data models 3,500 sequential pipeline builds recorded chronologically across 18 months of software evolution.

---

## 2. Feature Schema & Engineering

| Feature Name | Data Type | Source Stage | Description | Empirical Range |
|---|---|---|---|---|
| `build_id` | String | Identifier | Unique sequential build execution identifier | `BUILD-10000` to `BUILD-13499` |
| `timestamp` | ISO-8601 | Git Commit | Exact UTC timestamp of commit and build trigger | April 2025 – October 2026 |
| `commit_hash` | Hex String | Git | 8-character SHA1 commit identifier | Hash |
| `branch` | Categorical | Git | Originating Git branch (main, develop, feature/*) | 6 active branches |
| `files_changed` | Integer | Source Churn | Count of source files altered in the commit | 1 to 45 files |
| `lines_added` | Integer | Source Churn | Total new lines of code added | 1 to 1,500 lines |
| `lines_deleted` | Integer | Source Churn | Total lines of code removed | 0 to 800 lines |
| `test_count` | Integer | Test Suite | Size of the automated regression test suite | 25 to 160 test cases |
| `prev_runtime` | Float | Telemetry | Duration (seconds) of the immediately prior build | 8.5 to 135.0 seconds |
| `prev_failure` | Binary (0/1) | Telemetry | Whether the immediately prior build failed | 0 (Success) or 1 (Failure) |
| `cpu_usage` | Float | Telemetry | Peak runner CPU utilization percentage | 15.0% to 98.0% |
| `memory_usage` | Float | Telemetry | Peak runner RAM allocation in megabytes (MB) | 120.0 to 950.0 MB |
| `total_churn` | Integer | Engineered | Sum of `lines_added` and `lines_deleted` | 1 to 2,300 lines |
| `churn_per_file`| Float | Engineered | Code churn normalized by number of changed files | 0.5 to 150.0 lines/file |
| `add_del_ratio` | Float | Engineered | Ratio of additions to deletions $(\text{added}+1)/(\text{deleted}+1)$ | 0.05 to 50.0 |
| `actual_runtime`| Float | Target (Reg) | Real observed pipeline execution duration (seconds) | Continuous float |
| `build_failed` | Binary (0/1) | Target (Clf) | Real observed pipeline outcome: 0=Success, 1=Failure | ~22.5% failure prevalence |

---

## 3. Data Leakage Prevention Guarantee

To guarantee valid, deployable inference in a production CI/CD environment:
1. **Temporal Horizon Check:** Every input feature $X_i$ is strictly available *prior* to test suite execution.
2. **No Target Contamination:** Post-execution outcomes (`actual_runtime` and `build_failed`) are isolated as supervised targets $y$ and never mixed into the feature matrix.
3. **Chronological Splitting:** The data is split strictly in time order ($80\%$ historical training, $20\%$ forward testing). Standard random cross-validation shuffling is deliberately avoided to reflect genuine temporal forecasting.
4. **Scaler Isolation:** Normalization parameters (mean and standard deviation) are learned strictly on the historical training set (`train_df`) and persisted via `scaler.joblib` for unseen inference.
