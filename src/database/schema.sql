-- Database Schema: AI-Driven CI/CD Pipeline Optimization
-- Author: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore

CREATE TABLE IF NOT EXISTS builds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    build_id TEXT UNIQUE NOT NULL,
    timestamp TEXT NOT NULL,
    commit_hash TEXT,
    branch TEXT DEFAULT 'main',
    execution_mode TEXT NOT NULL, -- 'BASELINE' or 'AI_OPTIMIZED'
    execution_strategy TEXT NOT NULL, -- 'FULL_TEST_SUITE' or 'TARGETED_TEST_SUITE'
    status TEXT NOT NULL, -- 'SUCCESS' or 'FAILED'
    actual_runtime REAL NOT NULL,
    test_count INTEGER NOT NULL,
    tests_passed INTEGER NOT NULL,
    tests_failed INTEGER NOT NULL,
    cpu_usage REAL NOT NULL,
    memory_usage REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    build_id TEXT NOT NULL,
    failure_probability REAL NOT NULL,
    model_confidence REAL NOT NULL,
    predicted_runtime REAL NOT NULL,
    predicted_failure INTEGER NOT NULL,
    champion_classifier TEXT,
    champion_regressor TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (build_id) REFERENCES builds(build_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    build_id TEXT NOT NULL,
    execution_strategy TEXT NOT NULL,
    safety_triggered INTEGER NOT NULL, -- 0 or 1
    fallback_reason TEXT,
    decision_explanation TEXT NOT NULL,
    risk_threshold REAL NOT NULL,
    confidence_threshold REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (build_id) REFERENCES builds(build_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS build_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    build_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    change_type TEXT NOT NULL, -- 'ADDED', 'MODIFIED', 'DELETED'
    FOREIGN KEY (build_id) REFERENCES builds(build_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS build_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    build_id TEXT NOT NULL,
    test_path TEXT NOT NULL,
    status TEXT NOT NULL, -- 'PASSED', 'FAILED', 'SKIPPED'
    FOREIGN KEY (build_id) REFERENCES builds(build_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id TEXT UNIQUE NOT NULL,
    scenario_name TEXT NOT NULL,
    description TEXT,
    baseline_runtime REAL NOT NULL,
    optimized_runtime REAL NOT NULL,
    runtime_savings_pct REAL NOT NULL,
    baseline_tests_count INTEGER NOT NULL,
    optimized_tests_count INTEGER NOT NULL,
    test_reduction_pct REAL NOT NULL,
    baseline_cpu REAL NOT NULL,
    optimized_cpu REAL NOT NULL,
    baseline_memory REAL NOT NULL,
    optimized_memory REAL NOT NULL,
    defect_injected INTEGER DEFAULT 0,
    baseline_defect_detected INTEGER DEFAULT 0,
    optimized_defect_detected INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
