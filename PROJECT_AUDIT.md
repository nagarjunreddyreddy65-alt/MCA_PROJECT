# PROJECT AUDIT: AI-DRIVEN CI/CD PIPELINE OPTIMIZATION

**Student Name:** NAGARJUNREDDY  
**USN:** 1DS25MC052  
**Guide:** Prof. Mahendra Kumar B  
**Department:** Master of Computer Applications (MCA)  
**Institution:** Dayananda Sagar College of Engineering, Bangalore-560078  
**Academic Year:** 2026–2027  
**Date of Audit:** November 6, 2026  

---

## 1. Executive Summary

An exhaustive initial audit was conducted on the workspace `C:\PRO_1DS25MC052` and the host operating environment to determine existing assets, dependencies, and requirements before initiating development.

The project originates from the approved MCA Major Project Synopsis titled **"AI-DRIVEN CI/CD PIPELINE OPTIMIZATION"**. The primary mission is to develop, test, validate, and document a production-grade, reproducible AI-assisted DevOps framework that intelligently predicts CI/CD build failures and execution runtimes, conducts AST-based static source dependency analysis to select impacted tests, and executes a safety-aware decision engine to reduce pipeline runtime and computational overhead while guaranteeing zero silent test omissions and fail-safe fallback.

---

## 2. Workspace & Environment Inventory

### 2.1 Existing Files and Codebase
* **Workspace Directory:** `C:\PRO_1DS25MC052`
* **Pre-existing Code/Models/Data:** None in the workspace folder. The workspace was cleanly provisioned and has now been initialized as a clean Git repository (`main` branch) configured with author identity `NAGARJUNREDDY <1ds25mc052@dsce.edu.in>`.
* **External Reference Assets:**
  - `C:\DEVOPS_BENCHMARK_REPOS\click` and `C:\DEVOPS_BENCHMARK_REPOS\requests` exist on the host as real-world Python benchmark repositories with active test suites.

### 2.2 Installed Software & Tooling Environment
* **Operating System:** Windows 11 (build 10.0.26100), PowerShell shell
* **Python Runtime:** Python 3.14.0 (Installed at `C:\Program Files\Python314\python.exe`)
* **Git Version:** 2.55.0.windows.5
* **Docker CLI:** Docker version 29.7.2 (Daemon inactive; Dockerfiles and compose specs must be fully reproducible and executable)
* **Pre-installed Python Libraries:**
  - `scikit-learn` 1.9.1 (Machine learning algorithms, metrics, pipelines)
  - `pandas` 3.0.6 (Dataframe manipulation, data ingestion)
  - `numpy` 2.5.3 (Numerical computing)
  - `fastapi` 0.142.2 (REST API backend)
  - `uvicorn` 0.54.0 (ASGI server)
  - `pydantic` 2.13.5 (Data validation and schemas)
  - `joblib` 1.6.0 (Model serialization)
  - `matplotlib` 3.11.2 & `seaborn` 0.13.2 (Visualizations)
  - `psutil` 7.2.2 (System resource telemetry: CPU, memory, execution duration)
  - `pytest` 9.1.1 & `coverage` 7.16.2 (Automated test suites)
  - `reportlab` 5.0.1 & `pymupdf` 1.28.2 (PDF report generation engine)

---

## 3. Gap Analysis (What Exists vs. What Must Be Built)

| Component / Requirement | Status | Required Action |
|---|---|---|
| **Git Repository** | Initialized | Clean initial commit with baseline configuration |
| **Historical CI/CD Dataset** | Missing | Generate TravisTorrent-aligned and telemetry-grounded structured dataset with rigorous schema validation (code churn, test count, past runtime, past failure, CPU/memory) |
| **Data Engineering & Preprocessing** | Missing | Build data loading, missing value imputation, outlier analysis, chronological splitting, and EDA script with saved distribution plots |
| **ML Engine - Failure Classification** | Missing | Implement and benchmark Logistic Regression, Decision Tree, and Random Forest; compute Accuracy, Precision, Recall, F1, ROC-AUC, Confusion Matrix; serialize champion model |
| **ML Engine - Runtime Prediction** | Missing | Implement and benchmark Linear Regression, Random Forest Regressor, Gradient Boosting Regressor; compute MAE, MSE, RMSE, R²; serialize champion model |
| **Source-Code Change Analyzer (AST)** | Missing | Implement Git diff parsing + Python `ast` structural analyzer to extract classes, functions, imports, call graphs, and map modified code to test suites |
| **Test Selection Engine** | Missing | Implement impact-aware test selector with explicit fail-safe full-suite fallback logic for unknown files, empty mappings, or syntax errors |
| **Safety-Aware Decision Engine** | Missing | Implement strict synopsis thresholds: Failure Prob $\ge 0.70 \to \text{FULL}$, Confidence $< 0.65 \to \text{FULL}$, plus invalid/missing feature fallback |
| **FastAPI Backend & SQLite DB** | Missing | Build REST API endpoints for predictions, test selection, pipeline execution, telemetry ingestion, and SQLite persistent schema |
| **Interactive Dashboard** | Missing | Build responsive modern web dashboard with charts, real-time prediction forms, code change simulation, and baseline vs. AI comparative metrics |
| **GitHub Actions Workflows** | Missing | Create Baseline workflow (`.github/workflows/baseline.yml`) and AI-Optimized workflow (`.github/workflows/ai-optimized.yml`) |
| **Dockerization** | Missing | Write multi-stage Dockerfile and docker-compose.yml with persistent SQLite volume |
| **Automated Testing Suite** | Missing | Comprehensive pytest suite covering unit, integration, AST, ML, API, and safety fallback behavior |
| **Experimental Evaluation** | Missing | Execute controlled baseline vs. AI-optimized comparative experiments measuring runtime, test reduction, CPU, memory, defect detection |
| **Academic Deliverables** | Missing | Comprehensive MCA Project Report (DOCX/PDF), PowerPoint Presentation (PPTX/PDF), 50+ Viva Q&A, and Demonstration Script |

---

## 4. Key Architectural & Academic Principles

1. **Academic Honesty & Genuine Metrics:** Never fabricate prediction values, synthetic accuracy, or experimental measurements. All metrics must derive from actual model training and real pipeline executions.
2. **Fail-Safe, Not Fail-Open:** Low failure probability never permits skipping tests if AST mapping is ambiguous or model confidence is low. Software quality is preserved above all.
3. **No Unnecessary Generative AI:** Strict alignment with the synopsis: classical ML (ensemble learning, tree models, linear models), AST static analysis, and deterministic rule-based safety gating.
4. **End-to-End Demonstration:** The system must run locally and interactively from git commit to telemetry recording and dashboard visualization.
