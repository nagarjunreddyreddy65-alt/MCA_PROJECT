"""Data Preprocessing, Cleaning, Feature Engineering, and EDA Pipeline.
Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

import json
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import StandardScaler
import joblib

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import (
    DATA_RAW_DIR,
    DATA_PROCESSED_DIR,
    DATA_EDA_DIR,
    MODELS_DIR,
    FEATURE_COLUMNS,
    TARGET_FAILURE,
    TARGET_RUNTIME,
    RANDOM_SEED,
)

# Set non-interactive matplotlib backend
plt.switch_backend("Agg")


def load_raw_dataset(file_path: Path = None) -> pd.DataFrame:
    if file_path is None:
        file_path = DATA_RAW_DIR / "travisitorrent_cicd_raw.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"Raw dataset file not found at: {file_path}")
    df = pd.read_csv(file_path)
    return df


def clean_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    """Performs integrity checks, duplicate removal, and domain boundary validation."""
    initial_count = len(df)
    df = df.drop_duplicates(subset=["build_id", "commit_hash"])

    # Ensure chronological order
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by="timestamp").reset_index(drop=True)

    # Impute or drop nulls if any exist
    df = df.dropna(subset=FEATURE_COLUMNS + [TARGET_FAILURE, TARGET_RUNTIME])

    # Domain constraints validation
    df = df[df["files_changed"] > 0]
    df = df[df["lines_added"] >= 0]
    df = df[df["lines_deleted"] >= 0]
    df = df[df["test_count"] > 0]
    df = df[df["prev_runtime"] > 0]
    df = df[df["actual_runtime"] > 0]
    df = df[df["prev_failure"].isin([0, 1])]
    df = df[df["build_failed"].isin([0, 1])]
    df = df[(df["cpu_usage"] >= 0) & (df["cpu_usage"] <= 100)]
    df = df[(df["memory_usage"] >= 0) & (df["memory_usage"] <= 8192)]

    # Feature Engineering additions:
    # 1. Total Churn = lines_added + lines_deleted
    df["total_churn"] = df["lines_added"] + df["lines_deleted"]
    # 2. Churn per file ratio
    df["churn_per_file"] = df["total_churn"] / df["files_changed"].clip(lower=1)
    # 3. Addition to deletion ratio (prevent divide by zero with +1)
    df["add_del_ratio"] = (df["lines_added"] + 1) / (df["lines_deleted"] + 1)

    final_count = len(df)
    print(f"[*] Cleaned dataset: {final_count} valid records (retained {final_count/initial_count:.2%})")
    return df


def generate_eda_reports_and_plots(df: pd.DataFrame):
    """Generates distribution plots, correlation matrices, and summary statistics."""
    DATA_EDA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Summary Statistics Dictionary
    summary = {
        "total_records": int(len(df)),
        "failure_rate": float(df[TARGET_FAILURE].mean()),
        "success_rate": float(1.0 - df[TARGET_FAILURE].mean()),
        "runtime_mean": float(df[TARGET_RUNTIME].mean()),
        "runtime_std": float(df[TARGET_RUNTIME].std()),
        "runtime_median": float(df[TARGET_RUNTIME].median()),
        "feature_metrics": {},
    }

    for col in FEATURE_COLUMNS:
        summary["feature_metrics"][col] = {
            "mean": float(df[col].mean()),
            "std": float(df[col].std()),
            "min": float(df[col].min()),
            "25%": float(df[col].quantile(0.25)),
            "50%": float(df[col].median()),
            "75%": float(df[col].quantile(0.75)),
            "max": float(df[col].max()),
        }

    summary_file = DATA_EDA_DIR / "eda_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=4)
    print(f"[+] Saved EDA summary statistics: {summary_file}")

    # Set aesthetic style
    sns.set_theme(style="whitegrid", palette="muted")

    # 2. Feature Distributions Plot
    fig, axes = plt.subplots(2, 4, figsize=(18, 9))
    axes = axes.flatten()
    for idx, col in enumerate(FEATURE_COLUMNS):
        sns.histplot(df[col], kde=True, ax=axes[idx], color="#2563eb", bins=25)
        axes[idx].set_title(f"Distribution of {col}", fontsize=11, fontweight="bold")
        axes[idx].set_xlabel(col)
        axes[idx].set_ylabel("Frequency")
    plt.tight_layout()
    dist_plot_path = DATA_EDA_DIR / "feature_distributions.png"
    plt.savefig(dist_plot_path, dpi=300)
    plt.close()
    print(f"[+] Saved feature distributions plot: {dist_plot_path}")

    # 3. Correlation Heatmap
    plt.figure(figsize=(10, 8))
    numeric_cols = FEATURE_COLUMNS + [TARGET_FAILURE, TARGET_RUNTIME]
    corr_matrix = df[numeric_cols].corr()
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True)
    plt.title("Correlation Matrix: CI/CD Churn, Telemetry, and Targets", fontsize=13, fontweight="bold")
    plt.tight_layout()
    corr_plot_path = DATA_EDA_DIR / "correlation_matrix.png"
    plt.savefig(corr_plot_path, dpi=300)
    plt.close()
    print(f"[+] Saved correlation matrix plot: {corr_plot_path}")

    # 4. Failure Probability by Churn and Prior Failure
    plt.figure(figsize=(9, 5))
    df["churn_bracket"] = pd.qcut(df["lines_added"] + df["lines_deleted"], q=5, duplicates="drop")
    churn_analysis = df.groupby(["churn_bracket", "prev_failure"], observed=True)[TARGET_FAILURE].mean().reset_index()
    sns.barplot(
        data=churn_analysis,
        x="churn_bracket",
        y=TARGET_FAILURE,
        hue="prev_failure",
        palette={0: "#10b981", 1: "#ef4444"},
    )
    plt.title("Failure Probability by Code Churn & Prior Failure Status", fontsize=12, fontweight="bold")
    plt.xlabel("Code Churn Quantile Range (Lines Added + Deleted)")
    plt.ylabel("Observed Failure Rate")
    plt.xticks(rotation=20)
    plt.legend(title="Previous Build Failed", labels=["Prior Success (0)", "Prior Failure (1)"])
    plt.tight_layout()
    churn_plot_path = DATA_EDA_DIR / "failure_by_churn.png"
    plt.savefig(churn_plot_path, dpi=300)
    plt.close()
    print(f"[+] Saved churn vs failure plot: {churn_plot_path}")


def chronological_split_and_scale(
    df: pd.DataFrame, train_ratio: float = 0.80
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Splits dataset chronologically to reflect real CI/CD production deployment.
    Never shuffles historical time series to prevent forward-looking data leakage.
    """
    n_total = len(df)
    n_train = int(n_total * train_ratio)

    train_df = df.iloc[:n_train].copy().reset_index(drop=True)
    test_df = df.iloc[n_train:].copy().reset_index(drop=True)

    print(f"[*] Chronological Split: {len(train_df)} training samples, {len(test_df)} testing samples")

    # Fit scaler strictly on training features
    scaler = StandardScaler()
    scaler.fit(train_df[FEATURE_COLUMNS])

    # Save scaler for online inference
    scaler_path = MODELS_DIR / "scaler.joblib"
    joblib.dump(scaler, scaler_path)
    print(f"[+] Serialized feature scaler: {scaler_path}")

    # Save processed CSV files
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PROCESSED_DIR / "cicd_cleaned.csv", index=False)
    train_df.to_csv(DATA_PROCESSED_DIR / "cicd_train.csv", index=False)
    test_df.to_csv(DATA_PROCESSED_DIR / "cicd_test.csv", index=False)
    print(f"[+] Saved cleaned dataset: {DATA_PROCESSED_DIR / 'cicd_cleaned.csv'}")
    print(f"[+] Saved train dataset: {DATA_PROCESSED_DIR / 'cicd_train.csv'}")
    print(f"[+] Saved test dataset: {DATA_PROCESSED_DIR / 'cicd_test.csv'}")

    return train_df, test_df


def run_data_pipeline():
    print("=" * 60)
    print("AI-Driven CI/CD Optimization: Phase 1 Data Pipeline")
    print("=" * 60)
    raw_df = load_raw_dataset()
    cleaned_df = clean_and_validate(raw_df)
    generate_eda_reports_and_plots(cleaned_df)
    train_df, test_df = chronological_split_and_scale(cleaned_df)
    print("[SUCCESS] Phase 1 Data Engineering and EDA Pipeline Completed Successfully.")
    return train_df, test_df


if __name__ == "__main__":
    run_data_pipeline()
