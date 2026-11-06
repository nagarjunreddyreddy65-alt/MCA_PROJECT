# PROJECT STATUS: AI-DRIVEN CI/CD PIPELINE OPTIMIZATION

**Student Name:** NAGARJUNREDDY  
**USN:** 1DS25MC052  
**Guide:** Prof. Mahendra Kumar B  
**Department:** Master of Computer Applications (MCA)  
**Institution:** Dayananda Sagar College of Engineering, Bangalore  
**Academic Year:** 2026–2027  
**Last Updated:** November 6, 2026  

---

## Overall Module Status Matrix

| ID | Module / Component | Category | Status | Verification Evidence / Artifact |
|---|---|---|---|---|
| **M01** | Git Repository & Workspace Setup | Environment | **Verified** | Initialized `.git` on `main`, user credentials configured |
| **M02** | Initial Project Audit & Governance | Documentation | **Verified** | `PROJECT_AUDIT.md`, `IMPLEMENTATION_PLAN.md`, `PROJECT_STATUS.md`, `CHANGELOG.md` |
| **M03** | CI/CD Dataset Ingestion & Curation | Phase 1 (Data) | **Not Started** | `data/raw/`, `data/cleaned/`, schema validation |
| **M04** | Data Preprocessing & Feature Engineering | Phase 1 (Data) | **Not Started** | Preprocessing script, chronological train/test split |
| **M05** | Exploratory Data Analysis & Plots | Phase 1 (Data) | **Not Started** | EDA script, distribution & correlation charts in `data/eda/` |
| **M06** | Failure Classification Model Suite | Phase 2 (ML) | **Not Started** | Logistic Regression, Decision Tree, Random Forest trained |
| **M07** | Runtime Regression Model Suite | Phase 2 (ML) | **Not Started** | Linear Regression, Random Forest, Gradient Boosting trained |
| **M08** | Model Persistence & Evaluation Metrics | Phase 2 (ML) | **Not Started** | Joblib serialized models in `models/`, `model_metrics.json` |
| **M09** | Git Diff & File Churn Analyzer | Phase 3 (AST) | **Not Started** | `src/analyzer/git_diff.py` change detection |
| **M10** | Python AST Dependency Parser | Phase 3 (AST) | **Not Started** | `src/analyzer/ast_parser.py` symbol extraction |
| **M11** | Intelligent Test Selection Engine | Phase 4 (Selection) | **Not Started** | `src/selector/test_selector.py` with fallback safety |
| **M12** | Safety-Aware Decision Engine | Phase 5 (Safety) | **Not Started** | `src/decision/safety_engine.py` (0.70 risk, 0.65 conf rules) |
| **M13** | SQLite Telemetry Database Layer | Phase 6 (Backend) | **Not Started** | `src/database/schema.sql`, `db_manager.py` |
| **M14** | FastAPI REST Services | Phase 6 (Backend) | **Not Started** | `src/api/main.py` with 11+ endpoints |
| **M15** | Interactive DevOps Web Dashboard | Phase 7 (UI/UX) | **Not Started** | `src/dashboard/` responsive UI with Chart.js |
| **M16** | Conventional Baseline CI/CD Workflow | Phase 8 (DevOps) | **Not Started** | `.github/workflows/baseline.yml` |
| **M17** | AI-Optimized CI/CD Workflow | Phase 8 (DevOps) | **Not Started** | `.github/workflows/ai-optimized.yml` |
| **M18** | Docker & Docker Compose Containerization | Phase 8 (DevOps) | **Not Started** | `Dockerfile`, `docker-compose.yml`, `.dockerignore` |
| **M19** | Comprehensive Pytest Test Suite | Phase 9 (Testing) | **Not Started** | Unit, integration, safety fallback tests in `tests/` |
| **M20** | Controlled Experimental Evaluation | Phase 10 (Research) | **Not Started** | 10 comparative scenarios, mutation/defect injection |
| **M21** | Publication-Grade Visualizations | Phase 10 (Research) | **Not Started** | Runtime, test reduction, and CPU/memory plots |
| **M22** | Comprehensive Project Report (DOCX/PDF) | Phase 11 (Academic) | **Not Started** | 33-chapter formal MCA report conforming to DSCE synopsis |
| **M23** | Professional Presentation (PPTX/PDF) | Phase 11 (Academic) | **Not Started** | 18 slides with detailed speaker notes |
| **M24** | 50+ Viva Voce Questions & Answers | Phase 11 (Academic) | **Not Started** | Comprehensive technical viva prep guide |
| **M25** | Live Demonstration Guide & Script | Phase 11 (Academic) | **Not Started** | Step-by-step terminal execution instructions |

---

## Quality Gate Checklist

- [x] **Gate 0: Inspection & Planning** — Environment verified, git initialized, audit docs published.
- [ ] **Gate 1: Data Pipeline** — Dataset generated, preprocessed, split chronologically, validated.
- [ ] **Gate 2: Machine Learning** — 6 models trained, evaluated, saved, zero metric fabrication.
- [ ] **Gate 3: AST & Test Selection** — Static analysis works, dependency graph generated, test selection verified.
- [ ] **Gate 4: Safety Decision Engine** — Risk & confidence thresholds tested, fail-safe fallback verified.
- [ ] **Gate 5: Backend & Database** — FastAPI endpoints respond, SQLite telemetry persists across restarts.
- [ ] **Gate 6: Interactive Dashboard** — Live UI connected to backend, charts update with real data.
- [ ] **Gate 7: DevOps Automation** — GitHub Actions workflows validated, Docker setup complete.
- [ ] **Gate 8: Automated Pytest Suite** — 100% test pass rate with coverage report.
- [ ] **Gate 9: Empirical Validation** — 10 controlled scenarios, defect injection verified, genuine metrics reported.
- [ ] **Gate 10: Academic Deliverables** — Report, slides, viva Q&A, and demo script finalized.
