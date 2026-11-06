"""Pydantic Request and Response Schemas for FastAPI backend.
Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FeatureVectorInput(BaseModel):
    files_changed: int = Field(default=2, ge=1, description="Number of modified source files")
    lines_added: int = Field(default=45, ge=0, description="Total code lines added")
    lines_deleted: int = Field(default=12, ge=0, description="Total code lines deleted")
    test_count: int = Field(default=30, ge=1, description="Number of test cases in test suite")
    prev_runtime: float = Field(default=42.0, ge=0.0, description="Runtime in seconds of preceding build")
    prev_failure: int = Field(default=0, ge=0, le=1, description="1 if previous build failed, else 0")
    cpu_usage: float = Field(default=38.0, ge=0.0, le=100.0, description="Runner CPU usage percentage")
    memory_usage: float = Field(default=260.0, ge=0.0, description="Runner memory allocation in MB")


class FailurePredictionResponse(BaseModel):
    failure_probability: float
    predicted_failure: int
    model_confidence: float
    champion_classifier: str
    decision_hint: str


class RuntimePredictionResponse(BaseModel):
    predicted_runtime_sec: float
    champion_regressor: str


class ASTAnalysisRequest(BaseModel):
    app_dir: str = Field(default="sample_app")
    tests_dir: str = Field(default="sample_tests")


class TestSelectionRequest(BaseModel):
    changed_files: List[str] = Field(default_factory=lambda: ["sample_app/auth.py"])


class DecisionRequest(BaseModel):
    changed_files: List[str] = Field(default_factory=lambda: ["sample_app/auth.py"])
    features: Optional[FeatureVectorInput] = None
    risk_threshold: Optional[float] = None
    confidence_threshold: Optional[float] = None


class PipelineExecutionRequest(BaseModel):
    execution_mode: str = Field(default="AI_OPTIMIZED", description="BASELINE or AI_OPTIMIZED")
    changed_files: Optional[List[str]] = None
    features: Optional[FeatureVectorInput] = None
    branch: str = Field(default="main")
