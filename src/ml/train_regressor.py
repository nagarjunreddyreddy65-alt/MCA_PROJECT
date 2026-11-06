"""Runtime Regression Model Training & Evaluation.
Trains and benchmarks Linear Regression, Random Forest Regressor, and Gradient Boosting
for CI/CD pipeline execution duration prediction on historical telemetry.

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
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import (
    DATA_PROCESSED_DIR,
    MODELS_DIR,
    FEATURE_COLUMNS,
    TARGET_RUNTIME,
    RANDOM_SEED,
)

plt.switch_backend("Agg")


def train_runtime_regressors():
    print("=" * 65)
    print("AI-Driven CI/CD Optimization: Training Runtime Regressors")
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
    y_train = train_df[TARGET_RUNTIME].values
    X_test_raw = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_RUNTIME].values

    # Scaled feature matrices for linear regression
    X_train_scaled = scaler.transform(X_train_raw)
    X_test_scaled = scaler.transform(X_test_raw)

    # 1. Baseline Predictor (Mean predictor as scientific benchmark)
    dummy = DummyRegressor(strategy="mean")
    dummy.fit(X_train_raw, y_train)
    dummy_pred = dummy.predict(X_test_raw)
    baseline_mae = float(mean_absolute_error(y_test, dummy_pred))
    baseline_rmse = float(np.sqrt(mean_squared_error(y_test, dummy_pred)))
    baseline_r2 = float(r2_score(y_test, dummy_pred))
    print(f"[*] Baseline Predictor (Mean): MAE={baseline_mae:.2f}s, RMSE={baseline_rmse:.2f}s, R²={baseline_r2:.4f}")

    # 2. Candidate regression algorithms specified in MCA Synopsis Section 4.4
    models = {
        "Linear Regression": {
            "model": LinearRegression(),
            "use_scaled": True,
            "filename": "runtime_regressor_lr.joblib",
        },
        "Random Forest Regressor": {
            "model": RandomForestRegressor(
                n_estimators=120,
                max_depth=12,
                min_samples_split=6,
                min_samples_leaf=3,
                random_state=RANDOM_SEED,
                n_jobs=-1,
            ),
            "use_scaled": False,
            "filename": "runtime_regressor_rf.joblib",
        },
        "Gradient Boosting Regressor": {
            "model": GradientBoostingRegressor(
                n_estimators=140,
                learning_rate=0.08,
                max_depth=5,
                subsample=0.85,
                random_state=RANDOM_SEED,
            ),
            "use_scaled": False,
            "filename": "runtime_regressor_gb.joblib",
        },
    }

    results = {
        "Baseline (Mean)": {
            "mae": round(baseline_mae, 4),
            "mse": round(float(mean_squared_error(y_test, dummy_pred)), 4),
            "rmse": round(baseline_rmse, 4),
            "r2_score": round(baseline_r2, 4),
            "filename": "none",
        }
    }

    best_model_name = None
    best_rmse = float("inf")
    predictions_dict = {}

    for name, config in models.items():
        print(f"\n---> Training {name}...")
        reg = config["model"]
        X_tr = X_train_scaled if config["use_scaled"] else X_train_raw
        X_te = X_test_scaled if config["use_scaled"] else X_test_raw

        reg.fit(X_tr, y_train)
        y_pred = reg.predict(X_te)
        predictions_dict[name] = y_pred

        mae = float(mean_absolute_error(y_test, y_pred))
        mse = float(mean_squared_error(y_test, y_pred))
        rmse = float(np.sqrt(mse))
        r2 = float(r2_score(y_test, y_pred))

        results[name] = {
            "mae": round(mae, 4),
            "mse": round(mse, 4),
            "rmse": round(rmse, 4),
            "r2_score": round(r2, 4),
            "filename": config["filename"],
        }

        print(f"     MAE : {mae:.3f} seconds | RMSE: {rmse:.3f} seconds | R²: {r2:.4f}")

        # Persist model
        model_save_path = MODELS_DIR / config["filename"]
        joblib.dump(reg, model_save_path)
        print(f"     [+] Saved model: {model_save_path}")

        # Champion selection based on minimal RMSE
        if rmse < best_rmse:
            best_rmse = rmse
            best_model_name = name

    # Plot Actual vs. Predicted for champion model
    champion_preds = predictions_dict[best_model_name]
    plt.figure(figsize=(7, 6))
    plt.scatter(y_test, champion_preds, alpha=0.45, color="#2563eb", edgecolors="none")
    lims = [min(y_test.min(), champion_preds.min()) - 5, max(y_test.max(), champion_preds.max()) + 5]
    plt.plot(lims, lims, "r--", linewidth=2, label="Ideal 1:1 Identity Line")
    plt.xlim(lims)
    plt.ylim(lims)
    plt.xlabel("Actual Pipeline Execution Time (seconds)", fontsize=11)
    plt.ylabel(f"Predicted Runtime ({best_model_name})", fontsize=11)
    plt.title(f"Runtime Prediction: {best_model_name} (R² = {results[best_model_name]['r2_score']})", fontweight="bold")
    plt.legend()
    plt.tight_layout()
    scatter_path = MODELS_DIR / "regression_actual_vs_predicted.png"
    plt.savefig(scatter_path, dpi=300)
    plt.close()
    print(f"\n[+] Saved actual vs predicted plot: {scatter_path}")

    # Persist champion regressor alias
    champion_source = MODELS_DIR / models[best_model_name]["filename"]
    champion_dest = MODELS_DIR / "runtime_regressor_champion.joblib"
    joblib.dump(joblib.load(champion_source), champion_dest)
    print(f"[+] Selected Champion Regressor: {best_model_name} (Saved to {champion_dest})")

    return results, best_model_name


if __name__ == "__main__":
    train_runtime_regressors()
