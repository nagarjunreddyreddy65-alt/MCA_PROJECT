# CHANGELOG: AI-DRIVEN CI/CD PIPELINE OPTIMIZATION

All notable changes, milestone completions, architectural decisions, and verification activities are documented in this log.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.1.0] - 2026-11-10

### Host Laptop Multi-Application Integration
- **Multi-Repository Optimization Engine (`src/integration/multi_repo_optimizer.py`):**
  - Scans and detects external applications across the host laptop (`C:\Users\nagar\DEVOPS_NAGARJUN`, `C:\DEVOPS_BENCHMARK_REPOS\requests`, `C:\DEVOPS_BENCHMARK_REPOS\click`, `C:\Users\nagar\ci-experiment`).
  - Implements cross-repository AST static code dependency mapping and test extraction.
  - Generates change-aware test subsets for external codebases with up to 90.9% test churn reduction.
  - Provides workflow installation capability: injects `.github/workflows/ai-optimized-cicd.yml` and `ai_cicd_runner.py` directly into external repositories.
- **REST API Extensions (`src/api/main.py`):**
  - Added `/api/laptop/repositories`, `/api/laptop/analyze`, `/api/laptop/optimize`, and `/api/laptop/install`.
- **Interactive Dashboard Extension (`src/dashboard/`):**
  - Added Tab 8: **"💻 Laptop Applications Integration"** with live application grid and controller.
- **Verification & Testing (`scripts/test_laptop_integration.py`):**
  - Verified end-to-end integration across all 4 host laptop repositories.

## [1.0.0] - 2026-11-06

### Complete Major Academic Project Release
- **Environment & Setup:** Initialized Git repository on `main` branch with author identity `NAGARJUNREDDY <1ds25mc052@dsce.edu.in>`.
- **Phase 1: Dataset & Data Engineering:**
  - Synthesized 3,500 TravisTorrent-aligned historical CI/CD build records across 18 months of software evolution (`data/raw/travisitorrent_cicd_raw.csv`).
  - Implemented data validation, cleaning, and chronological 80/20 train/test splitting (2,800 train, 700 test).
  - Fitted `StandardScaler` on training set only (`models/scaler.joblib`) to eliminate data leakage.
  - Generated EDA distribution histograms, correlation heatmaps, and churn-failure bar charts in `data/eda/`.
- **Phase 2: Machine Learning Engine:**
  - Trained and benchmarked Logistic Regression, Decision Tree, and Random Forest classifiers on `build_failed`. Selected Random Forest as champion (Failure Recall = 74.12%, F1 = 0.5248, ROC-AUC = 0.6533).
  - Trained and benchmarked Linear Regression, Random Forest Regressor, and Gradient Boosting Regressor on `actual_runtime`. Selected Linear Regression as champion (MAE = 5.31s, RMSE = 7.19s, $R^2 = 0.6187$).
  - Serialized all 6 candidate models and champions with `joblib` into `models/`.
  - Compiled master evaluation metrics into `models/model_metrics.json`.
- **Phase 3: Source Code AST Dependency Analysis:**
  - Implemented `GitDiffAnalyzer` (`src/analyzer/git_diff.py`) detecting file additions, modifications, and lines churned.
  - Implemented `ASTDependencyAnalyzer` (`src/analyzer/ast_parser.py`) extracting classes, functions, and imports with transitive dependency propagation.
- **Phase 4: Intelligent Test Selection Engine:**
  - Implemented `TestSelectionEngine` (`src/selector/test_selector.py`) mapping modified code to targeted tests.
  - Implemented 5-tier fail-safe fallback to full test suite for non-code files, syntax errors, unmapped modules, or empty selections.
- **Phase 5: Safety-Aware Decision Engine:**
  - Implemented `SafetyDecisionEngine` (`src/decision/safety_engine.py`) strictly enforcing synopsis rules:
    - Failure Risk $\ge 0.70 \implies$ FULL TEST SUITE.
    - Model Confidence $< 0.65 \implies$ FULL TEST SUITE.
    - Low Risk + High Confidence $\implies$ TARGETED TEST SUITE approved.
- **Phase 6: Backend & Database:**
  - Designed relational SQLite schema (`schema.sql`) and `DatabaseManager` (`src/database/db_manager.py`).
  - Built `PipelineRunner` (`src/runner/pipeline_runner.py`) profiling duration, CPU %, and memory allocation via `psutil`.
  - Built FastAPI application (`src/api/main.py`) with 11 production REST endpoints.
- **Phase 7: Interactive DevOps Dashboard:**
  - Developed responsive single-page dashboard (`src/dashboard/index.html`, `style.css`, `app.js`).
  - Created 7 tabs: Overview KPIs, AI Predictor, AST Visualizer, Safety Engine, Live Runner, Model Benchmarks, Empirical Experiments.
- **Phase 8: DevOps Automation & Docker:**
  - Created GitHub Actions conventional baseline workflow (`.github/workflows/baseline.yml`).
  - Created GitHub Actions AI-optimized workflow (`.github/workflows/ai-optimized.yml`).
  - Authored production multi-stage `Dockerfile` and `docker-compose.yml` with persistent SQLite volume.
- **Phase 9: Automated Testing Suite:**
  - Authored 37 automated pytest tests in `tests/` covering unit, integration, AST, ML, API, and safety fallbacks.
  - Achieved 100% pass rate (37 passed in 7.76s).
- **Phase 10: Empirical Validation:**
  - Executed 10 controlled scenarios (`experiments/run_experiments.py`) comparing Baseline vs. AI-Optimized pipelines.
  - Validated mutation defect injection in `inventory.py`: achieved 100% defect retention concordance (zero escaped bugs).
  - Measured up to 63.33% test reduction and real runtime savings.
  - Saved publication charts in `experiments/plots/` (`runtime_comparison.png`, `test_reduction.png`, `resource_consumption.png`).
- **Phase 11: Academic Project Deliverables:**
  - Published 33-chapter formal Project Report (`docs/FINAL_PROJECT_REPORT.md` and compiled PDF `docs/FINAL_PROJECT_REPORT.pdf`).
  - Published 18-slide presentation deck with detailed speaker notes (`docs/PRESENTATION_SLIDES.md` and compiled widescreen PDF `docs/PRESENTATION_SLIDES.pdf`).
  - Published 50+ viva voce examination guide (`docs/VIVA_QUESTIONS.md`).
  - Published step-by-step practical demonstration guide (`docs/DEMONSTRATION_GUIDE.md`).
  - Published comprehensive `README.md`.
