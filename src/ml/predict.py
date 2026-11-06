"""Unified Machine Learning Inference Service.
Loads persisted champion models to compute failure probability, model confidence,
and estimated pipeline execution duration with strict validation.

Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

from pathlib import Path
import sys
from typing import Any, Dict, Optional, Tuple
import joblib
import numpy as np
import pandas as pd

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import (
    MODELS_DIR,
    FEATURE_COLUMNS,
    FAILURE_PROBABILITY_THRESHOLD,
    CONFIDENCE_THRESHOLD,
)


class MLPredictionEngine:
    """Production ML Inference Engine managing classifier, regressor, and scaler."""

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or MODELS_DIR
        self.classifier = None
        self.regressor = None
        self.scaler = None
        self.is_loaded = False
        self.load_models()

    def load_models(self) -> bool:
        """Loads champion classifier, regressor, and feature scaler from disk."""
        clf_path = self.models_dir / "failure_classifier_champion.joblib"
        reg_path = self.models_dir / "runtime_regressor_champion.joblib"
        scaler_path = self.models_dir / "scaler.joblib"

        if not (clf_path.exists() and reg_path.exists() and scaler_path.exists()):
            self.is_loaded = False
            return False

        try:
            self.classifier = joblib.load(clf_path)
            self.regressor = joblib.load(reg_path)
            self.scaler = joblib.load(scaler_path)
            self.is_loaded = True
            return True
        except Exception as e:
            print(f"[!] Error loading ML models: {e}")
            self.is_loaded = False
            return False

    def validate_features(self, features: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Strictly validates input feature dictionary against schema."""
        for col in FEATURE_COLUMNS:
            if col not in features:
                return False, f"Missing required feature: {col}"
            val = features[col]
            if val is None or not isinstance(val, (int, float, np.number)):
                return False, f"Feature '{col}' must be a numerical value, got {type(val)}"
            if val < 0 and col not in ["lines_deleted"]:
                return False, f"Feature '{col}' cannot be negative: {val}"

        # Specific bounds checks
        if features["files_changed"] < 1:
            return False, "files_changed must be at least 1"
        if features["prev_failure"] not in [0, 1, 0.0, 1.0]:
            return False, "prev_failure must be binary 0 or 1"
        if not (0 <= features["cpu_usage"] <= 100):
            return False, "cpu_usage must be between 0 and 100 percent"
        if not (0 <= features["memory_usage"] <= 16384):
            return False, "memory_usage out of realistic bounds"

        return True, None

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Generates failure risk and runtime predictions from feature dict.

        Returns structured prediction dictionary:
        {
            "valid": bool,
            "failure_probability": float (0.0 to 1.0),
            "predicted_failure": int (0 or 1),
            "model_confidence": float (0.0 to 1.0),
            "predicted_runtime": float (seconds),
            "error": Optional[str]
        }
        """
        if not self.is_loaded:
            # Attempt reload
            if not self.load_models():
                return {
                    "valid": False,
                    "failure_probability": 1.0,  # Fail-safe high risk
                    "predicted_failure": 1,
                    "model_confidence": 0.0,     # Fail-safe low confidence
                    "predicted_runtime": 120.0,
                    "error": "ML models not loaded or missing from disk.",
                }

        is_valid, err_msg = self.validate_features(features)
        if not is_valid:
            return {
                "valid": False,
                "failure_probability": 1.0,
                "predicted_failure": 1,
                "model_confidence": 0.0,
                "predicted_runtime": 120.0,
                "error": f"Invalid feature input: {err_msg}",
            }

        try:
            # Construct feature DataFrame
            feature_row = pd.DataFrame([{col: features[col] for col in FEATURE_COLUMNS}])

            # Classification inference
            if hasattr(self.classifier, "predict_proba"):
                probs = self.classifier.predict_proba(feature_row)[0]
                prob_fail = float(probs[1])
            else:
                pred_label = self.classifier.predict(feature_row)[0]
                prob_fail = 1.0 if pred_label == 1 else 0.0

            # Model Confidence calculation:
            # High certainty when probability approaches 0.0 or 1.0; lowest certainty near 0.5
            # Range: [0.0, 1.0] where 1.0 = absolute certainty, 0.0 = maximal equivocation
            confidence = round(float(2.0 * abs(prob_fail - 0.5)), 4)
            pred_fail = 1 if prob_fail >= 0.50 else 0

            # Runtime Regression inference
            # If regressor expects scaled data (like linear regression), scale it; otherwise use raw
            if "LinearRegression" in type(self.regressor).__name__:
                X_scaled = self.scaler.transform(feature_row)
                pred_runtime = float(self.regressor.predict(X_scaled)[0])
            else:
                pred_runtime = float(self.regressor.predict(feature_row)[0])

            # Ensure lower bound on runtime (setup overhead)
            pred_runtime = max(8.0, round(pred_runtime, 2))

            return {
                "valid": True,
                "failure_probability": round(prob_fail, 4),
                "predicted_failure": pred_fail,
                "model_confidence": confidence,
                "predicted_runtime": pred_runtime,
                "error": None,
            }

        except Exception as e:
            return {
                "valid": False,
                "failure_probability": 1.0,
                "predicted_failure": 1,
                "model_confidence": 0.0,
                "predicted_runtime": 120.0,
                "error": f"Exception during ML inference: {str(e)}",
            }


# Singleton instance for application reuse
prediction_engine = MLPredictionEngine()
