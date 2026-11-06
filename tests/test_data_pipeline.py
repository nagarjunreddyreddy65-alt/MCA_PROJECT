"""Unit tests for CI/CD dataset generation, cleaning, and preprocessing."""

import pytest
import pandas as pd
from src.config import FEATURE_COLUMNS, TARGET_FAILURE, TARGET_RUNTIME
from src.data.generate_dataset import generate_cicd_dataset
from src.data.preprocess import clean_and_validate


def test_generate_cicd_dataset_schema():
    df = generate_cicd_dataset(n_samples=50, random_seed=123)
    assert len(df) == 50
    for col in FEATURE_COLUMNS:
        assert col in df.columns
    assert TARGET_FAILURE in df.columns
    assert TARGET_RUNTIME in df.columns


def test_generate_cicd_dataset_value_constraints():
    df = generate_cicd_dataset(n_samples=100, random_seed=456)
    assert (df["files_changed"] >= 1).all()
    assert (df["lines_added"] >= 0).all()
    assert (df["lines_deleted"] >= 0).all()
    assert (df["test_count"] > 0).all()
    assert (df["actual_runtime"] > 0).all()
    assert df["build_failed"].isin([0, 1]).all()
    assert ((df["cpu_usage"] >= 0) & (df["cpu_usage"] <= 100)).all()
    assert ((df["memory_usage"] >= 0) & (df["memory_usage"] <= 8192)).all()


def test_clean_and_validate():
    raw_df = generate_cicd_dataset(n_samples=60, random_seed=789)
    cleaned = clean_and_validate(raw_df)
    assert len(cleaned) == 60
    assert "total_churn" in cleaned.columns
    assert "churn_per_file" in cleaned.columns
    assert "add_del_ratio" in cleaned.columns
