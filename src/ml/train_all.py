"""Orchestration script for training and benchmarking all ML models.
Generates comprehensive evaluation matrices and writes models/model_metrics.json.

Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

import json
from pathlib import Path
import sys

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import MODELS_DIR
from src.ml.train_classifier import train_failure_classifiers
from src.ml.train_regressor import train_runtime_regressors


def train_and_evaluate_all():
    print("\n" + "#" * 70)
    print("PHASE 2: COMPREHENSIVE MACHINE LEARNING MODEL TRAINING & BENCHMARKING")
    print("#" * 70 + "\n")

    # 1. Train Classification Models
    clf_results, champion_clf = train_failure_classifiers()

    # 2. Train Regression Models
    reg_results, champion_reg = train_runtime_regressors()

    # 3. Compile Master Metrics Document
    master_metrics = {
        "project": "AI-Driven CI/CD Pipeline Optimization",
        "author": "NAGARJUNREDDY (1DS25MC052)",
        "institution": "Dayananda Sagar College of Engineering, Bangalore",
        "champion_classification_model": champion_clf,
        "champion_regression_model": champion_reg,
        "classification_benchmarks": clf_results,
        "regression_benchmarks": reg_results,
    }

    metrics_file = MODELS_DIR / "model_metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(master_metrics, f, indent=4)
    print(f"\n[+] Master model metrics saved to: {metrics_file}")

    # Print summary benchmark table
    print("\n" + "=" * 70)
    print("CLASSIFICATION BENCHMARK SUMMARY (Failure Prediction)")
    print("=" * 70)
    print(f"{'Algorithm':<26} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'ROC-AUC':<10}")
    print("-" * 88)
    for name, m in clf_results.items():
        is_champ = " *" if name == champion_clf else "  "
        print(f"{name + is_champ:<26} | {m['accuracy']:<10.4f} | {m['precision']:<10.4f} | {m['recall']:<10.4f} | {m['f1_score']:<10.4f} | {m['roc_auc']:<10.4f}")

    print("\n" + "=" * 70)
    print("REGRESSION BENCHMARK SUMMARY (Runtime Prediction)")
    print("=" * 70)
    print(f"{'Algorithm':<28} | {'MAE (s)':<10} | {'RMSE (s)':<10} | {'R² Score':<10}")
    print("-" * 65)
    for name, m in reg_results.items():
        is_champ = " *" if name == champion_reg else "  "
        print(f"{name + is_champ:<28} | {m['mae']:<10.4f} | {m['rmse']:<10.4f} | {m['r2_score']:<10.4f}")
    print("\n* Denotes selected champion production model.")


if __name__ == "__main__":
    train_and_evaluate_all()
