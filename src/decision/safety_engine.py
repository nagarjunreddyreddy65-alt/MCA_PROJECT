"""Safety-Aware Decision Engine.
Implements the multi-tiered safety gating specified in MCA Synopsis Section 4.1 Stage 9.
Guarantees fail-safe fallback to full regression testing whenever risk is high,
confidence is low, or dependency mapping is ambiguous.

Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

import datetime
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import (
    FAILURE_PROBABILITY_THRESHOLD,
    CONFIDENCE_THRESHOLD,
    STRATEGY_FULL_SUITE,
    STRATEGY_TARGETED,
)
from src.ml.predict import prediction_engine
from src.selector.test_selector import test_selector


class SafetyDecisionEngine:
    """Combines ML predictive risk with AST test selection under strict safety rules."""

    def __init__(
        self,
        risk_threshold: float = FAILURE_PROBABILITY_THRESHOLD,
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
    ):
        self.risk_threshold = risk_threshold
        self.confidence_threshold = confidence_threshold

    def evaluate(
        self,
        changed_files: List[str],
        features: Optional[Dict[str, Any]] = None,
        override_risk_threshold: Optional[float] = None,
        override_confidence_threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Evaluates pipeline risk, tests selection, and safety gating.

        Returns comprehensive decision record:
        - execution_strategy: FULL_TEST_SUITE | TARGETED_TEST_SUITE
        - failure_probability: float
        - model_confidence: float
        - predicted_runtime: float
        - selected_tests: List[str]
        - changed_files: List[str]
        - safety_triggered: bool
        - decision_explanation: str
        - fallback_reason: Optional[str]
        - timestamp: ISO-8601 string
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        risk_thresh = override_risk_threshold if override_risk_threshold is not None else self.risk_threshold
        conf_thresh = override_confidence_threshold if override_confidence_threshold is not None else self.confidence_threshold

        # Step 1: Execute AST-based Test Selection
        test_selection_res = test_selector.select_tests(changed_files)
        all_tests = test_selection_res["all_tests"]
        targeted_candidate = test_selection_res["selected_tests"]

        # Step 2: Check AST selection fallback condition
        if test_selection_res["fallback_active"]:
            # AST fallback triggered (syntax error, unknown file, missing mapping, etc.)
            pred_res = (
                prediction_engine.predict(features)
                if features
                else {
                    "failure_probability": 0.50,
                    "model_confidence": 0.50,
                    "predicted_runtime": 60.0,
                    "error": None,
                }
            )
            return {
                "execution_strategy": STRATEGY_FULL_SUITE,
                "failure_probability": pred_res["failure_probability"],
                "model_confidence": pred_res["model_confidence"],
                "predicted_runtime": pred_res["predicted_runtime"],
                "selected_tests": all_tests,
                "all_tests": all_tests,
                "total_tests_count": len(all_tests),
                "selected_tests_count": len(all_tests),
                "test_reduction_percentage": 0.0,
                "safety_triggered": True,
                "decision_explanation": f"FULL TEST SUITE ENFORCED (AST Fallback): {test_selection_res['fallback_reason']}",
                "fallback_reason": test_selection_res["fallback_reason"],
                "changed_files": changed_files,
                "affected_modules": test_selection_res.get("affected_modules", []),
                "timestamp": timestamp,
            }

        # Step 3: Execute ML Inference
        if not features:
            # Fallback if no features provided
            return {
                "execution_strategy": STRATEGY_FULL_SUITE,
                "failure_probability": 1.0,
                "model_confidence": 0.0,
                "predicted_runtime": 80.0,
                "selected_tests": all_tests,
                "all_tests": all_tests,
                "total_tests_count": len(all_tests),
                "selected_tests_count": len(all_tests),
                "test_reduction_percentage": 0.0,
                "safety_triggered": True,
                "decision_explanation": "FULL TEST SUITE ENFORCED: Missing input telemetry features for ML risk assessment.",
                "fallback_reason": "Missing telemetry features.",
                "changed_files": changed_files,
                "affected_modules": test_selection_res.get("affected_modules", []),
                "timestamp": timestamp,
            }

        pred_res = prediction_engine.predict(features)

        # Fallback Check: Prediction failure or model error
        if not pred_res["valid"]:
            return {
                "execution_strategy": STRATEGY_FULL_SUITE,
                "failure_probability": 1.0,
                "model_confidence": 0.0,
                "predicted_runtime": 90.0,
                "selected_tests": all_tests,
                "all_tests": all_tests,
                "total_tests_count": len(all_tests),
                "selected_tests_count": len(all_tests),
                "test_reduction_percentage": 0.0,
                "safety_triggered": True,
                "decision_explanation": f"FULL TEST SUITE ENFORCED: ML inference error ({pred_res.get('error')}). Fail-safe policy active.",
                "fallback_reason": pred_res.get("error"),
                "changed_files": changed_files,
                "affected_modules": test_selection_res.get("affected_modules", []),
                "timestamp": timestamp,
            }

        fail_prob = pred_res["failure_probability"]
        confidence = pred_res["model_confidence"]
        pred_runtime = pred_res["predicted_runtime"]

        # Step 4: Apply Synopsis Safety Policy Rules
        # Rule 1: High Failure Risk
        if fail_prob >= risk_thresh:
            explanation = (
                f"FULL TEST SUITE ENFORCED (High Risk): Predicted failure probability ({fail_prob:.2%}) "
                f"meets or exceeds risk safety threshold ({risk_thresh:.2%}). Running complete suite to prevent regression."
            )
            return {
                "execution_strategy": STRATEGY_FULL_SUITE,
                "failure_probability": fail_prob,
                "model_confidence": confidence,
                "predicted_runtime": pred_runtime,
                "selected_tests": all_tests,
                "all_tests": all_tests,
                "total_tests_count": len(all_tests),
                "selected_tests_count": len(all_tests),
                "test_reduction_percentage": 0.0,
                "safety_triggered": True,
                "decision_explanation": explanation,
                "fallback_reason": f"Predicted failure risk ({fail_prob:.2%}) >= threshold ({risk_thresh:.2%})",
                "changed_files": changed_files,
                "affected_modules": test_selection_res.get("affected_modules", []),
                "timestamp": timestamp,
            }

        # Rule 2: Low Model Confidence
        if confidence < conf_thresh:
            explanation = (
                f"FULL TEST SUITE ENFORCED (Low Confidence): Model confidence ({confidence:.2%}) "
                f"falls below minimum certainty threshold ({conf_thresh:.2%}). Fallback to full testing."
            )
            return {
                "execution_strategy": STRATEGY_FULL_SUITE,
                "failure_probability": fail_prob,
                "model_confidence": confidence,
                "predicted_runtime": pred_runtime,
                "selected_tests": all_tests,
                "all_tests": all_tests,
                "total_tests_count": len(all_tests),
                "selected_tests_count": len(all_tests),
                "test_reduction_percentage": 0.0,
                "safety_triggered": True,
                "decision_explanation": explanation,
                "fallback_reason": f"Model confidence ({confidence:.2%}) < threshold ({conf_thresh:.2%})",
                "changed_files": changed_files,
                "affected_modules": test_selection_res.get("affected_modules", []),
                "timestamp": timestamp,
            }

        # Step 5: Safe for Targeted Test Execution!
        # Both safety conditions satisfied: Low failure risk AND High model confidence
        reduction_count = len(all_tests) - len(targeted_candidate)
        reduction_pct = round((reduction_count / len(all_tests)) * 100.0, 2)
        explanation = (
            f"TARGETED TEST EXECUTION APPROVED: Failure probability is low ({fail_prob:.2%} < {risk_thresh:.2%}) "
            f"and model confidence is high ({confidence:.2%} >= {conf_thresh:.2%}). "
            f"Executing {len(targeted_candidate)} targeted tests out of {len(all_tests)} ({reduction_pct}% reduction)."
        )

        return {
            "execution_strategy": STRATEGY_TARGETED,
            "failure_probability": fail_prob,
            "model_confidence": confidence,
            "predicted_runtime": pred_runtime,
            "selected_tests": targeted_candidate,
            "all_tests": all_tests,
            "total_tests_count": len(all_tests),
            "selected_tests_count": len(targeted_candidate),
            "test_reduction_percentage": reduction_pct,
            "safety_triggered": False,
            "decision_explanation": explanation,
            "fallback_reason": None,
            "changed_files": changed_files,
            "affected_modules": test_selection_res.get("affected_modules", []),
            "timestamp": timestamp,
        }


# Global singleton
safety_engine = SafetyDecisionEngine()
