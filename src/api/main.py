"""FastAPI Application Server for AI-Driven CI/CD Pipeline Optimization.
Serves REST API endpoints and hosts the interactive monitoring dashboard.

Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
Supervisor: Prof. Mahendra Kumar B
"""

import json
from pathlib import Path
import sys
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import BASE_DIR, MODELS_DIR
from src.api.schemas import (
    FeatureVectorInput,
    FailurePredictionResponse,
    RuntimePredictionResponse,
    ASTAnalysisRequest,
    TestSelectionRequest,
    DecisionRequest,
    PipelineExecutionRequest,
)
from src.ml.predict import prediction_engine
from src.analyzer.git_diff import git_analyzer
from src.analyzer.ast_parser import ast_analyzer
from src.selector.test_selector import test_selector
from src.decision.safety_engine import safety_engine
from src.database.db_manager import db_manager
from src.runner.pipeline_runner import pipeline_runner
from src.integration.multi_repo_optimizer import multi_repo_optimizer

app = FastAPI(
    title="AI-Driven CI/CD Pipeline Optimization API",
    description="MCA Major Project API - Predictive CI/CD Risk, AST Test Selection & Safety Telemetry",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for open demonstration access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Dashboard Directory
DASHBOARD_DIR = BASE_DIR / "src" / "dashboard"
if DASHBOARD_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(DASHBOARD_DIR)), name="static")


@app.get("/", include_in_schema=False)
def serve_dashboard():
    index_path = DASHBOARD_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse({"message": "AI-Driven CI/CD Pipeline Optimization API is running. Visit /docs for Swagger."})


@app.get("/api/health")
def health_check():
    """Checks service health, model availability, and database connectivity."""
    db_connected = False
    try:
        db_manager.get_connection().close()
        db_connected = True
    except Exception:
        db_connected = False

    return {
        "status": "healthy" if (prediction_engine.is_loaded and db_connected) else "degraded",
        "models_loaded": prediction_engine.is_loaded,
        "database_connected": db_connected,
        "champion_classifier": "Random Forest",
        "champion_regressor": "Linear Regression",
        "version": "1.0.0",
        "student": "NAGARJUNREDDY (1DS25MC052)",
        "guide": "Prof. Mahendra Kumar B",
        "institution": "Dayananda Sagar College of Engineering, Bangalore",
    }


@app.get("/api/overview")
def get_overview_kpis():
    """Returns overview KPI cards for the dashboard."""
    return db_manager.get_overview_kpis()


@app.post("/api/predict/failure", response_model=FailurePredictionResponse)
def predict_pipeline_failure(input_data: FeatureVectorInput):
    """Predicts pipeline failure probability and model confidence."""
    features = input_data.model_dump()
    res = prediction_engine.predict(features)
    if not res["valid"]:
        raise HTTPException(status_code=400, detail=res.get("error"))

    prob = res["failure_probability"]
    hint = "High Risk - Recommend Full Test Suite" if prob >= 0.70 else "Low Risk - Candidate for Test Optimization"

    return FailurePredictionResponse(
        failure_probability=prob,
        predicted_failure=res["predicted_failure"],
        model_confidence=res["model_confidence"],
        champion_classifier="Random Forest",
        decision_hint=hint,
    )


@app.post("/api/predict/runtime", response_model=RuntimePredictionResponse)
def predict_pipeline_runtime(input_data: FeatureVectorInput):
    """Estimates expected pipeline runtime duration in seconds."""
    features = input_data.model_dump()
    res = prediction_engine.predict(features)
    if not res["valid"]:
        raise HTTPException(status_code=400, detail=res.get("error"))

    return RuntimePredictionResponse(
        predicted_runtime_sec=res["predicted_runtime"],
        champion_regressor="Linear Regression",
    )


@app.post("/api/analyze/git")
def analyze_git_workspace():
    """Inspects active git workspace for modified files and code churn."""
    return git_analyzer.extract_git_features()


@app.post("/api/analyze/ast")
def analyze_ast_dependencies(req: ASTAnalysisRequest = ASTAnalysisRequest()):
    """Parses application modules and test files to build the AST dependency graph."""
    return ast_analyzer.build_test_dependency_map(
        app_dir=req.app_dir, tests_dir=req.tests_dir
    )


@app.post("/api/select/tests")
def select_tests_endpoint(req: TestSelectionRequest):
    """Selects targeted tests with full fallback safety."""
    return test_selector.select_tests(req.changed_files)


@app.post("/api/decision")
def evaluate_decision_engine(req: DecisionRequest):
    """Evaluates ML risk prediction and AST test selection under the synopsis safety rules."""
    features_dict = req.features.model_dump() if req.features else None
    return safety_engine.evaluate(
        changed_files=req.changed_files,
        features=features_dict,
        override_risk_threshold=req.risk_threshold,
        override_confidence_threshold=req.confidence_threshold,
    )


@app.post("/api/pipeline/execute")
def execute_pipeline(req: PipelineExecutionRequest):
    """Executes either Baseline (full suite) or AI-Optimized pipeline with live telemetry."""
    if req.execution_mode.upper() == "BASELINE":
        res = pipeline_runner.run_baseline_pipeline(branch=req.branch)
    else:
        features_dict = req.features.model_dump() if req.features else None
        res = pipeline_runner.run_optimized_pipeline(
            changed_files=req.changed_files,
            override_features=features_dict,
            branch=req.branch,
        )
    return res


@app.get("/api/telemetry/history")
def get_telemetry_history(limit: int = 50):
    """Returns past pipeline build executions with predictions and resource measurements."""
    return db_manager.get_build_history(limit=limit)


@app.get("/api/models/metrics")
def get_model_metrics():
    """Returns model benchmark statistics and evaluation records."""
    metrics_path = MODELS_DIR / "model_metrics.json"
    if metrics_path.exists():
        try:
            return json.loads(metrics_path.read_text(encoding="utf-8"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read model metrics: {e}")
    raise HTTPException(status_code=404, detail="Model metrics file not found. Train models first.")


@app.get("/api/experiments/comparison")
def get_experiment_comparison():
    """Returns comparative evaluation records (Baseline vs AI-Optimized)."""
    return db_manager.get_experiments()


@app.get("/api/laptop/repositories")
def list_laptop_repositories():
    """Discovers and lists accessible applications and repositories on the laptop."""
    return multi_repo_optimizer.discover_laptop_repositories()


@app.post("/api/laptop/analyze")
def analyze_laptop_repository(payload: Dict[str, Any]):
    """Runs AST analysis and symbol dependency mapping on any laptop repository."""
    repo_path = payload.get("path")
    if not repo_path:
        raise HTTPException(status_code=400, detail="Missing required 'path' field.")
    try:
        return multi_repo_optimizer.analyze_external_repo(repo_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/laptop/optimize")
def optimize_laptop_repository(payload: Dict[str, Any]):
    """Applies AI-driven change detection, ML risk prediction, and test selection to any laptop repo."""
    repo_path = payload.get("path")
    changed_files = payload.get("changed_files")
    if not repo_path:
        raise HTTPException(status_code=400, detail="Missing required 'path' field.")
    try:
        return multi_repo_optimizer.optimize_external_repo_change(repo_path, changed_files=changed_files)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/laptop/install")
def install_ai_cicd_to_laptop_repo(payload: Dict[str, Any]):
    """Installs the AI CI/CD workflow and runner script into any laptop repository."""
    repo_path = payload.get("path")
    if not repo_path:
        raise HTTPException(status_code=400, detail="Missing required 'path' field.")
    try:
        return multi_repo_optimizer.install_ai_cicd_to_repo(repo_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)
