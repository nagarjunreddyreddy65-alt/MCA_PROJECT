"""Configuration parameters for AI-Driven CI/CD Pipeline Optimization.
Project: Major MCA Project, Dayananda Sagar College of Engineering
Student: NAGARJUNREDDY (1DS25MC052)
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_EDA_DIR = DATA_DIR / "eda"
MODELS_DIR = BASE_DIR / "models"
EXPERIMENTS_DIR = BASE_DIR / "experiments"
EXPERIMENTS_RESULTS_DIR = EXPERIMENTS_DIR / "results"
EXPERIMENTS_PLOTS_DIR = EXPERIMENTS_DIR / "plots"
DOCS_DIR = BASE_DIR / "docs"
SRC_DIR = BASE_DIR / "src"

# Database Path
DATABASE_PATH = BASE_DIR / "cicd_telemetry.db"

# Feature definitions aligned with MCA Synopsis
FEATURE_COLUMNS = [
    "files_changed",
    "lines_added",
    "lines_deleted",
    "test_count",
    "prev_runtime",
    "prev_failure",
    "cpu_usage",
    "memory_usage",
]

TARGET_FAILURE = "build_failed"
TARGET_RUNTIME = "actual_runtime"

# Safety Policy Thresholds (Strictly defined in MCA Project Synopsis Section 4.1 Stage 9)
FAILURE_PROBABILITY_THRESHOLD = 0.70
CONFIDENCE_THRESHOLD = 0.65

# Execution Strategies
STRATEGY_FULL_SUITE = "FULL_TEST_SUITE"
STRATEGY_TARGETED = "TARGETED_TEST_SUITE"

# Random Seed for Reproducibility
RANDOM_SEED = 42

# Ensure directories exist
for directory in [
    DATA_RAW_DIR,
    DATA_PROCESSED_DIR,
    DATA_EDA_DIR,
    MODELS_DIR,
    EXPERIMENTS_RESULTS_DIR,
    EXPERIMENTS_PLOTS_DIR,
    DOCS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)
