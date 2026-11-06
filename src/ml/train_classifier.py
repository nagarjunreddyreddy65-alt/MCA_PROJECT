"""Failure Classification Model Training & Evaluation.
Trains and benchmarks Logistic Regression, Decision Tree, and Random Forest
for CI/CD build failure prediction on historical TravisTorrent-aligned data.

Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

import json
from pathlib import Path
import sys
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import (
    DATA_PROCESSED_DIR,
    MODELS_DIR,
    FEATURE_COLUMNS,
    TARGET_FAILURE,
    RANDOM_SEED,
)

plt.switch_backend("Agg")


def train_failure_classifiers():
    print("=" * 65)
    print("AI-Driven CI/CD Optimization: Training Failure Classifiers")
    print("=" * 65)

    train_path = DATA_PROCESSED_DIR / "cicd_train.csv"
    test_path = DATA_PROCESSED_DIR / "cicd_test.csv"
    scaler_path = MODELS_DIR / "scaler.joblib"

    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError("Processed datasets missing. Run preprocess.py first.")

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    scaler = joblib.load(scaler_path)

    X_train_raw = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_FAILURE].values
    X_test_raw = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_FAILURE].values

    # Scale feature matrices
    X_train_scaled = scaler.transform(X_train_raw)
    X_test_scaled = scaler.transform(X_test_raw)

    print(f"[*] Training samples: {len(X_train_scaled)}, Test samples: {len(X_test_scaled)}")
    print(f"[*] Failure prevalence - Train: {y_train.mean():.2%}, Test: {y_test.mean():.2%}")

    # Initialize candidate algorithms specified in MCA Synopsis Section 4.4
    models = {
        "Logistic Regression": {
            "model": LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=RANDOM_SEED,
            ),
            "use_scaled": True,
            "filename": "failure_classifier_lr.joblib",
        },
        "Decision Tree": {
            "model": DecisionTreeClassifier(
                max_depth=6,
                min_samples_split=10,
                min_samples_leaf=5,
                class_weight="balanced",
                random_state=RANDOM_SEED,
            ),
            "use_scaled": False,
            "filename": "failure_classifier_dt.joblib",
        },
        "Random Forest": {
            "model": RandomForestClassifier(
                n_estimators=120,
                max_depth=10,
                min_samples_split=8,
                min_samples_leaf=4,
                class_weight="balanced",
                random_state=RANDOM_SEED,
                n_jobs=-1,
            ),
            "use_scaled": False,
            "filename": "failure_classifier_rf.joblib",
        },
    }

    results = {}
    best_model_name = None
    best_f1 = -1.0

    plt.figure(figsize=(8, 6))

    for name, config in models.items():
        print(f"\n---> Training {name}...")
        clf = config["model"]
        X_tr = X_train_scaled if config["use_scaled"] else X_train_raw
        X_te = X_test_scaled if config["use_scaled"] else X_test_raw

        clf.fit(X_tr, y_train)

        # Predictions
        y_pred = clf.predict(X_te)
        y_prob = clf.predict_proba(X_te)[:, 1]

        # Calculate metrics
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        roc_auc = float(roc_auc_score(y_test, y_prob))
        cm = confusion_matrix(y_test, y_pred).tolist()

        results[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "confusion_matrix": cm,
            "filename": config["filename"],
        }

        print(f"     Accuracy : {acc:.4f} | Precision: {prec:.4f}")
        print(f"     Recall   : {rec:.4f} | F1-Score : {f1:.4f} | ROC-AUC: {roc_auc:.4f}")

        # Persist candidate model
        model_save_path = MODELS_DIR / config["filename"]
        joblib.dump(clf, model_save_path)
        print(f"     [+] Saved model: {model_save_path}")

        # Plot ROC curve
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        plt.plot(fpr, tpr, label=f"{name} (AUC = {roc_auc:.3f})")

        # Track champion model based on F1-Score (balances precision and recall for imbalanced CI failures)
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name

    # Finalize ROC plot
    plt.plot([0, 1], [0, 1], "k--", label="Random Chance (AUC = 0.500)")
    plt.xlabel("False Positive Rate (1 - Specificity)")
    plt.ylabel("True Positive Rate (Recall / Sensitivity)")
    plt.title("ROC Curves: CI/CD Build Failure Classification", fontsize=12, fontweight="bold")
    plt.legend(loc="lower right")
    plt.tight_layout()
    roc_plot_path = MODELS_DIR / "classification_roc_curves.png"
    plt.savefig(roc_plot_path, dpi=300)
    plt.close()
    print(f"\n[+] Saved ROC curves plot: {roc_plot_path}")

    # Plot Confusion Matrix for Champion Model
    champion_cm = results[best_model_name]["confusion_matrix"]
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        champion_cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Predicted Success", "Predicted Failure"],
        yticklabels=["Actual Success", "Actual Failure"],
    )
    plt.title(f"Confusion Matrix: {best_model_name} (Champion)", fontsize=11, fontweight="bold")
    plt.tight_layout()
    cm_plot_path = MODELS_DIR / "champion_confusion_matrix.png"
    plt.savefig(cm_plot_path, dpi=300)
    plt.close()
    print(f"[+] Saved Champion Confusion Matrix: {cm_plot_path}")

    # Persist champion model alias
    champion_source = MODELS_DIR / models[best_model_name]["filename"]
    champion_dest = MODELS_DIR / "failure_classifier_champion.joblib"
    joblib.dump(joblib.load(champion_source), champion_dest)
    print(f"[+] Selected Champion Classifier: {best_model_name} (Saved to {champion_dest})")

    return results, best_model_name


if __name__ == "__main__":
    train_failure_classifiers()
