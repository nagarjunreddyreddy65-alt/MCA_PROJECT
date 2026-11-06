# VIVA VOCE EXAMINATION GUIDE: 50+ QUESTIONS & ANSWERS
## AI-DRIVEN CI/CD PIPELINE OPTIMIZATION

**Student Name:** NAGARJUNREDDY  
**USN:** 1DS25MC052  
**Guide:** Prof. Mahendra Kumar B  
**Department:** Master of Computer Applications (MCA)  
**Institution:** Dayananda Sagar College of Engineering, Bangalore-560078  
**Academic Year:** 2026–2027  

---

### Category 1: Project Overview & Core Motivation

#### Q1. What is the core problem that your MCA project addresses?
**Answer:** Conventional CI/CD pipelines follow a static, unadaptive execution strategy: whenever a commit occurs, the entire regression test suite is executed regardless of the size, location, or risk of the code change. In large repositories, this results in excessive pipeline runtime, inflated cloud compute costs, CPU/RAM contention, and delayed developer feedback. My project addresses this by developing an AI-driven, change-aware CI/CD optimization framework that predicts pipeline risk and runtime, statically determines affected tests using Abstract Syntax Trees (AST), and applies a safety-aware decision engine to run a targeted test subset while guaranteeing that reliability is never compromised.

#### Q2. Why is your project an "AI-Driven DevOps" project rather than a "Generative AI" project?
**Answer:** The objective is deterministic, verifiable operational decision-making. Generative AI/LLMs introduce non-determinism, token latency, and hallucination risks, which are inappropriate for critical build/release gating. Our project strictly utilizes supervised machine learning (Random Forest, Logistic Regression, Gradient Boosting) for numerical risk and duration prediction, deterministic Abstract Syntax Tree (AST) parsing for structural dependency mapping, and formal rule-based safety thresholds.

#### Q3. What is the central research hypothesis of your project?
**Answer:** That combining predictive ML models trained on historical build telemetry with AST-based source code dependency analysis and multi-tier safety gating can significantly reduce unnecessary test executions and pipeline runtime without increasing defect escape rates.

#### Q4. What are the primary objectives accomplished in this work?
**Answer:**
1. Curation of a 3,500-build historical CI/CD dataset based on TravisTorrent empirical schemas.
2. Training and benchmark evaluation of 3 classification algorithms and 3 regression algorithms.
3. Development of Python AST dependency analysis with transitive symbol mapping.
4. Implementation of an intelligent test selector with 5-tier fail-safe full-suite fallback.
5. Design of a safety-aware decision engine enforcing synopsis thresholds (Risk $\ge 0.70 \to$ Full Suite, Confidence $< 0.65 \to$ Full Suite).
6. Building a persistent SQLite telemetry store and FastAPI REST backend.
7. Development of an interactive 7-tab DevOps monitoring dashboard.
8. Implementation of GitHub Actions workflows and Docker containerization.
9. Controlled empirical validation across 10 scenarios demonstrating 100% defect retention.

---

### Category 2: Machine Learning Engine

#### Q5. What features constitute the input vector $X$ for your ML models?
**Answer:** Based on Section 4.1 Stage 3 of our approved synopsis, the feature vector is:
$X = [\text{files\_changed}, \text{lines\_added}, \text{lines\_deleted}, \text{test\_count}, \text{prev\_runtime}, \text{prev\_failure}, \text{cpu\_usage}, \text{memory\_usage}]$.
All features are strictly measurable *prior* to test execution to eliminate data leakage.

#### Q6. What classification algorithms did you evaluate for pipeline failure prediction?
**Answer:** We evaluated:
1. **Logistic Regression:** Linear log-odds baseline model.
2. **Decision Tree Classifier:** Non-linear rule-based tree model.
3. **Random Forest Classifier:** Ensemble of 120 bagging decision trees with balanced class weighting.
Random Forest was selected as champion due to its high failure recall (74.12%), F1-score (0.5248), and ROC-AUC (0.6533).

#### Q7. Why is Failure Recall more important than raw Accuracy in CI/CD failure prediction?
**Answer:** CI/CD datasets are naturally class-imbalanced (~75% successes vs ~25% failures). A naive model predicting "Success" on every build achieves 75% accuracy but has 0% recall, causing catastrophic false negatives (predicting a build will pass when it actually fails). In CI/CD, a false negative risks shipping broken code to production. Therefore, model selection prioritizes Recall and F1-score with balanced class weights to penalize false negatives.

#### Q8. What regression algorithms did you evaluate for runtime prediction?
**Answer:** We evaluated:
1. **Baseline Predictor (Mean):** Scientific baseline predicting historical mean runtime ($\text{MAE} = 26.56$s, $R^2 = -5.20$).
2. **Linear Regression:** Champion regressor ($\text{MAE} = 5.31$s, $\text{RMSE} = 7.19$s, $R^2 = 0.6187$).
3. **Random Forest Regressor:** Non-linear ensemble ($\text{MAE} = 5.61$s, $R^2 = 0.5872$).
4. **Gradient Boosting Regressor:** Sequential boosting ensemble ($\text{MAE} = 5.76$s, $R^2 = 0.5771$).

#### Q9. How do you prevent data leakage during data preprocessing and training?
**Answer:**
1. Features are strictly pre-execution metrics.
2. The dataset is split chronologically ($80\%$ train, $20\%$ test) rather than randomly shuffled, preserving the time-series nature of continuous integration.
3. The `StandardScaler` is fitted exclusively on the historical training set and persisted using `joblib` to scale unseen commits during inference.

#### Q10. How is Model Confidence mathematically calculated in your system?
**Answer:** Model confidence is derived from the predicted failure probability $P(\text{failure})$:
$$\text{Confidence} = 2 \times |P(\text{failure}) - 0.5|$$
When the model predicts $P = 0.50$ (maximum equivocation), confidence is $0.0$. When $P \to 1.0$ or $P \to 0.0$, confidence approaches $1.0$ ($100\%$). If confidence falls below the $0.65$ synopsis threshold, safety gating activates.

---

### Category 3: AST Source-Code & Test Selection Analysis

#### Q11. What is an Abstract Syntax Tree (AST), and why did you use it?
**Answer:** An AST is a tree representation of the abstract syntactic structure of source code. Python's native `ast` module parses Python files into AST nodes without executing the code. We inspect `ast.ClassDef`, `ast.FunctionDef`, `ast.Import`, `ast.ImportFrom`, and `ast.Call` to extract exported symbols, inter-module dependencies, and test mappings statically.

#### Q12. What is transitive dependency resolution in your test selector?
**Answer:** If module $A$ (e.g., `payment.py`) imports module $B$ (e.g., `auth.py`), and test $T$ tests $A$, then any change to $B$ can break $A$. Our AST analyzer resolves transitive dependencies so that modifying `auth.py` automatically selects both `test_auth.py` and `test_payment.py`.

#### Q13. Under what conditions does the Test Selector enforce mandatory fallback to the FULL TEST SUITE?
**Answer:**
1. **Non-Python / Configuration Changes:** Changes to Dockerfiles, YAML, requirements.txt, or environment files.
2. **AST Parse / Syntax Errors:** If a modified Python file fails syntax validation.
3. **Unmapped Modules:** If a modified Python file has no corresponding test mapping.
4. **Empty Test Selection:** If AST resolution yields 0 tests despite code changes.
5. **Cross-Cutting Core Changes:** If a shared utility module affects $\ge 80\%$ of modules.

---

### Category 4: Safety-Aware Decision Engine

#### Q14. What are the exact thresholds enforced by the Safety Engine?
**Answer:** Strictly adhering to Section 4.1 Stage 9 of the approved synopsis:
- **Failure Risk Threshold:** If predicted failure probability $P(\text{failure}) \ge 0.70 \implies \text{FULL TEST SUITE}$.
- **Confidence Threshold:** If model confidence $< 0.65 \implies \text{FULL TEST SUITE}$.
- **Targeted Test Execution:** Only approved if $P < 0.70$ AND Confidence $\ge 0.65$ AND AST mapping is unambiguous.

#### Q15. Why is the system designed as "fail-safe" rather than "fail-open"?
**Answer:** In software quality assurance, safety is paramount. If the ML model is missing, inputs are corrupted, confidence is low, or dependencies are ambiguous, a "fail-open" system would skip tests, risking defect escape. Our system is "fail-safe": any anomaly, threshold breach, or ambiguity automatically defaults to running 100% of the regression test suite.

---

### Category 5: Backend, Telemetry & Dashboard Architecture

#### Q16. Why did you choose FastAPI over Flask or Django?
**Answer:** FastAPI provides native ASGI asynchronous performance, automatic OpenAPI/Swagger documentation, strict type validation via Pydantic schemas, and lightweight overhead ideal for CI/CD microservices and telemetry ingestion.

#### Q17. How does your SQLite telemetry persistence work?
**Answer:** We implemented a relational schema comprising `builds`, `predictions`, `decisions`, `build_files`, `build_tests`, and `experiments`. The database persists on disk (`cicd_telemetry.db`), surviving server restarts and container recycles via Docker volume mounting.

#### Q18. How does the interactive dashboard communicate with the backend?
**Answer:** The frontend dashboard (`index.html`, `style.css`, `app.js`) is served directly by FastAPI. It makes REST calls to `/api/health`, `/api/overview`, `/api/predict/*`, `/api/analyze/*`, `/api/decision`, `/api/pipeline/execute`, and `/api/experiments/comparison`, rendering dynamic Chart.js visualizations.

---

### Category 6: DevOps, Docker & GitHub Actions

#### Q19. Describe your two GitHub Actions workflows.
**Answer:**
1. **Conventional Baseline (`baseline.yml`):** Runs on push/PR, checks out code, installs dependencies, executes the full test suite via Pytest, and records execution metrics.
2. **AI-Optimized (`ai-optimized.yml`):** Runs on push/PR, checks out code with git history, analyzes git churn, extracts pre-execution features, invokes ML prediction, performs AST test selection, applies safety gating, executes either targeted or full tests, and uploads SQLite telemetry artifacts.

#### Q20. How is Docker utilized in this project?
**Answer:** We created a multi-stage `Dockerfile` and `docker-compose.yml`. It containerizes the Python runtime, dependencies, trained models, AST analyzer, and FastAPI server, mounting `cicd_telemetry.db` as a persistent volume and exposing port 8000 with a health check.

---

### Category 7: Empirical Results & Academic Validation

#### Q21. How did you validate that targeted testing does not miss bugs?
**Answer:** In Phase 10, Scenario 7, we performed deliberate defect injection (mutation defect in `sample_app/inventory.py`). Both the Baseline pipeline and the AI-Optimized pipeline caught the defect ($100\%$ defect retention concordance). Zero defects escaped.

#### Q22. What were the quantitative findings of your 10 experimental scenarios?
**Answer:**
- Mean Baseline Runtime: 1.76 seconds.
- Mean AI-Optimized Runtime: 1.67 seconds (up to 53.33% test reduction in targeted scenarios like `SCEN-02`).
- Safety Gating Activations: 7 out of 10 scenarios triggered safety gating due to high churn, syntax error, config files, or broad dependencies, proving the system is genuinely conservative and fail-safe.
- Defect Retention Rate: $100.0\%$.

#### Q23. What are the limitations of your system?
**Answer:**
1. Dynamic reflection, runtime metaprogramming (`eval`, `getattr`), and external database queries cannot be completely resolved through static AST parsing alone.
2. The current prototype focuses on Python codebases; multi-language projects require language-specific parsers.
3. Cold-start repositories without historical CI build logs require a baseline accumulation period before ML models can be trained.

#### Q24. What are the future enhancements for this project?
**Answer:** As outlined in the synopsis:
1. Extending AST analysis to Java, Go, TypeScript, and C#.
2. Integrating Large Language Models (LLMs) strictly for natural language commit message and requirement semantic understanding.
3. Dynamic Kubernetes container resource allocation based on predicted runtime.
4. Reinforcement learning for adaptive threshold tuning.
