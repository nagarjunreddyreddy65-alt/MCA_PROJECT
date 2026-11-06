# FINAL ACADEMIC PRESENTATION SLIDES & SPEAKER NOTES
## AI-DRIVEN CI/CD PIPELINE OPTIMIZATION

**Student Name:** NAGARJUNREDDY (USN: 1DS25MC052)  
**Project Guide:** Prof. Mahendra Kumar B  
**Department:** Master of Computer Applications (MCA)  
**Institution:** Dayananda Sagar College of Engineering, Bangalore-560078  
**Academic Year:** 2026–2027  

---

### SLIDE 1: Title & Candidacy
- **Title:** AI-Driven CI/CD Pipeline Optimization
- **Subtitle:** An Intelligent, Change-Aware, and Safety-Gated Continuous Integration Testing Framework
- **Candidate:** NAGARJUNREDDY (USN: 1DS25MC052)
- **Guide:** Prof. Mahendra Kumar B, Department of MCA
- **Institution:** Dayananda Sagar College of Engineering, Bangalore

> **Speaker Notes:**
> "Respected examiners, faculty members, and my project guide Prof. Mahendra Kumar B, good morning. I am Nagarjunreddy, USN 1DS25MC052, from the Department of MCA, Dayananda Sagar College of Engineering. Today, I present my major academic project titled 'AI-Driven CI/CD Pipeline Optimization'. This research develops an automated framework that combines supervised machine learning, static Abstract Syntax Tree analysis, and a safety-aware decision engine to eliminate redundant test executions and accelerate CI/CD release cycles without compromising software reliability."

---

### SLIDE 2: Introduction & Industry Context
- **The DevOps Paradigm:** Continuous Integration and Continuous Deployment (CI/CD) automates build, test, and release cycles.
- **The Static Execution Flaw:** Conventional pipelines blindly execute the entire regression test suite on every developer commit.
- **The Scalability Bottleneck:** As repositories grow to thousands of tests, pipeline execution times soar, inflating cloud costs and delaying developer feedback.
- **The AI Opportunity:** Historical build telemetry and source code changes can be analyzed to make pipeline execution adaptive and intelligent.

> **Speaker Notes:**
> "Continuous Integration has revolutionized agile software delivery. However, conventional CI/CD pipelines follow a static, unadaptive execution pattern. Whether a developer modifies a single isolated string in a localized module or refactors the entire core payment subsystem, the pipeline blindly executes 100% of the regression test suite. In enterprise environments, this causes severe feedback delays and exorbitant compute costs. Our mission is to transform CI/CD pipelines from static scripts into intelligent, adaptive systems."

---

### SLIDE 3: Problem Statement
- **Unnecessary Test Execution:** Running hundreds of unrelated tests for minor, localized changes.
- **Inflated Cycle Time:** Prolonged CI queue delays and slow developer feedback loops.
- **Resource Inefficiency:** High CPU utilization and memory contention on cloud runners.
- **Absence of Historical Context:** Past build outcomes, failure recurrence, and runner performance are discarded.
- **Unsafe Heuristics:** Existing test selection tools lack formal safety fallbacks when model confidence is low.

> **Speaker Notes:**
> "The central problem is twofold: first, unnecessary test execution wastes computational resources; second, existing research attempts at test selection often fail to provide fail-safe guarantees. When predictive models have low certainty, or when non-code files are altered, blind test omission causes defect escape. We formulate this problem: How can we reduce CI/CD test churn and execution time while providing an absolute fail-safe guarantee that defect detection capability is never compromised?"

---

### SLIDE 4: Project Objectives
- Curate and preprocess a 3,500-sample TravisTorrent-aligned CI/CD historical build dataset.
- Train and benchmark supervised ML classifiers for build failure risk prediction.
- Train and benchmark regression models for execution runtime forecasting.
- Perform static source-code dependency analysis using Python Abstract Syntax Trees (AST).
- Design a change-aware test selection engine with transitive dependency resolution.
- Implement a safety-aware decision engine enforcing synopsis thresholds ($P \ge 0.70$ or Confidence $< 0.65$).
- Develop a persistent SQLite telemetry store, FastAPI backend, and 7-tab monitoring dashboard.
- Validate through 10 controlled empirical scenarios, including mutation defect injection.

> **Speaker Notes:**
> "To address this challenge, we defined clear, measurable objectives aligned with our approved MCA project synopsis. These encompass data engineering, machine learning modeling, static code AST analysis, safety policy gating, full-stack REST and dashboard implementation, and empirical validation with defect injection."

---

### SLIDE 5: Existing System vs. Proposed System
| Dimension | Conventional Existing CI/CD | Proposed AI-Driven CI/CD Framework |
|---|---|---|
| **Execution Trigger** | Static; 100% test suite runs on every commit | Adaptive; targeted test subset selected based on churn |
| **Risk Awareness** | None; blind execution | ML predicts failure probability before execution |
| **Duration Forecast**| None; unpredictable duration | ML estimates expected runtime in seconds |
| **Dependency Analysis**| None; no code-to-test mapping | Static AST extracts direct & transitive dependencies |
| **Safety Gating** | Rigid; lacks fallback policies | Fail-safe: Risk $\ge 0.70$ or Conf $< 0.65 \to$ Full Suite |
| **Telemetry** | Ephemeral runner logs | Persistent SQLite schema & live monitoring dashboard |

> **Speaker Notes:**
> "This slide contrasts conventional CI/CD against our proposed system. While conventional pipelines execute blind static scripts, our system acts as an intelligent pipeline governor: predicting failure probability, analyzing code changes via AST, and applying deterministic safety rules to decide whether a targeted test suite is safe or if full regression testing must be enforced."

---

### SLIDE 6: System Architecture & Workflow
- **Developer Commit:** Git tracks modified files and calculates code churn (additions/deletions).
- **Feature Extraction:** Formulates pre-execution vector $X$ from churn and historical telemetry.
- **AI Prediction Engine:** Random Forest Classifier computes failure risk; Linear Regressor estimates duration.
- **AST Static Analysis:** Parses Python syntax trees to map modified code to test files transitively.
- **Safety Decision Engine:** Enforces multi-tier safety gating before selecting execution strategy.
- **Execution & Telemetry:** Pytest profiler tracks duration, CPU %, and memory; persists to SQLite.
- **Monitoring UI:** FastAPI backend serves live metrics to the responsive DevOps dashboard.

> **Speaker Notes:**
> "Here is our complete system architecture. Notice that every step is fully automated and deterministic. Features extracted from git diff are fed into our ML models. Simultaneously, the AST analyzer parses the modified code structure. Both outputs converge at the Safety Decision Engine. If any risk or uncertainty is detected, the engine defaults to the full test suite. If approved, targeted tests run, and real telemetry is stored in SQLite."

---

### SLIDE 7: Dataset & Data Engineering (Phase 1)
- **Empirical Grounding:** Modeled after the landmark TravisTorrent dataset (Beller et al., MSR 2017).
- **Dataset Size:** 3,500 chronological CI build records over 18 months of software evolution.
- **Feature Vector $X$:**
  $$X = [\text{files\_changed}, \text{lines\_added}, \text{lines\_deleted}, \text{test\_count}, \text{prev\_runtime}, \text{prev\_failure}, \text{cpu\_usage}, \text{memory\_usage}]$$
- **Class Balance:** 75.63% Success, 24.37% Failure (reflects empirical open-source CI distributions).
- **Leakage Prevention:** Chronological 80/20 train/test split (2,800 train, 700 test); scaler fitted strictly on train set.

> **Speaker Notes:**
> "For data engineering, we synthesized an authentic 3,500-sample dataset aligned with the TravisTorrent schema. To ensure scientific validity and eliminate data leakage, all features represent metrics available strictly *prior* to test execution. Furthermore, we split the data chronologically rather than randomly shuffling, preserving the time-series reality of continuous integration."

---

### SLIDE 8: ML Engine — Build Failure Classification (Phase 2)
- **Algorithms Evaluated:** Logistic Regression, Decision Tree, Random Forest Classifier.
- **Benchmark Metrics on 700 Held-out Test Builds:**
  - *Logistic Regression:* Accuracy = 50.00%, Recall = 84.65%, F1 = 0.5245, ROC-AUC = 0.6698
  - *Decision Tree:* Accuracy = 47.57%, Recall = 79.82%, F1 = 0.4979, ROC-AUC = 0.6180
  - *Random Forest (Champion):* Accuracy = 56.29%, Precision = 0.4062, **Recall = 74.12%**, **F1 = 0.5248**, **ROC-AUC = 0.6533**
- **Core Principle:** Failure Recall is prioritized over raw accuracy to prevent false negatives in CI release gating.

> **Speaker Notes:**
> "In Phase 2, we benchmarked three classification algorithms. Because build failures represent a minority class (~24%), raw accuracy is misleading. A naive classifier predicting success achieves 75% accuracy but zero recall. We optimized for Failure Recall and F1-score with balanced class weights. Random Forest was selected as champion because it achieved a strong 74.12% failure recall while maintaining the highest precision and F1-score."

---

### SLIDE 9: ML Engine — Runtime Regression (Phase 2)
- **Algorithms Evaluated:** Baseline (Mean), Linear Regression, Random Forest Regressor, Gradient Boosting.
- **Benchmark Metrics on 700 Held-out Test Builds:**
  - *Baseline Mean Predictor:* MAE = 26.56 s, RMSE = 28.97 s, $R^2 = -5.20$
  - *Linear Regression (Champion):* **MAE = 5.31 s**, **RMSE = 7.19 s**, **$R^2 = 0.6187$**
  - *Random Forest Regressor:* MAE = 5.61 s, RMSE = 7.48 s, $R^2 = 0.5872$
  - *Gradient Boosting Regressor:* MAE = 5.76 s, RMSE = 7.57 s, $R^2 = 0.5771$
- **Outcome:** Linear Regression reduced mean prediction error by **80.0%** compared to baseline error.

> **Speaker Notes:**
> "For runtime estimation, Linear Regression emerged as champion, cutting mean absolute prediction error from 26.56 seconds down to just 5.31 seconds, with an R-squared of 0.6187. Its microsecond inference time makes it ideal for real-time runner scheduling."

---

### SLIDE 10: AST Source-Code Dependency Analysis (Phase 3)
- **Static Syntax Tree Inspection:** Utilizes Python's native `ast` library to parse source files safely.
- **Symbol Extraction:** Harvests declared classes (`ClassDef`), functions (`FunctionDef`), and imports (`Import`, `ImportFrom`).
- **Transitive Dependency Resolution:**
  - Example: `payment.py` imports `auth.py`.
  - When `auth.py` is modified, the AST analyzer automatically links both `test_auth.py` and `test_payment.py`.
- **Syntax Error Trapping:** Safely traps `SyntaxError` during parsing and triggers immediate fail-safe fallback.

> **Speaker Notes:**
> "Phase 3 implements our AST static analysis. Rather than running slow runtime trace tools, we parse source code into Abstract Syntax Trees. The system extracts declared symbols and tracks import relationships. Crucially, it resolves transitive dependencies: if payment depends on auth, changing auth automatically queues payment tests, ensuring inter-module regressions are caught."

---

### SLIDE 11: Intelligent Test Selection & Fallbacks (Phase 4)
- **Targeted Selection:** Isolates the minimal sufficient test subset mapped to changed modules.
- **5-Tier Fail-Safe Fallback Triggers (Forcing Full Suite):**
  1. *Non-Python modifications:* Changes to `Dockerfile`, `requirements.txt`, `.yaml`.
  2. *AST Syntax Errors:* Unparseable code syntax.
  3. *Unmapped Modules:* Newly added Python files lacking registered tests.
  4. *Empty Selection:* Zero mapped tests returned.
  5. *Core Structural Changes:* Modifications to shared utilities affecting $\ge 80\%$ of modules.
- **Guaranteed Invariant:** Never silently drop or skip tests under ambiguity!

> **Speaker Notes:**
> "Phase 4 governs test selection. The core philosophy here is: 'Fail-safe, not fail-open'. If a developer changes a Dockerfile or requirements.txt, AST cannot map tests, so it immediately enforces full regression testing. If a file has a syntax error or has no tests, full testing is enforced. We never silently drop tests."

---

### SLIDE 12: Safety-Aware Decision Engine (Phase 5)
- **Direct Alignment with Synopsis Section 4.1 Stage 9:**
  - **Rule 1 (High Failure Risk):**
    $$\text{Failure Probability } P(\text{fail}) \ge 0.70 \implies \textbf{FULL TEST SUITE}$$
  - **Rule 2 (Low Model Confidence):**
    $$\text{Model Confidence } < 0.65 \implies \textbf{FULL TEST SUITE}$$
  - **Rule 3 (Targeted Execution Approved):**
    $$P(\text{fail}) < 0.70 \land \text{Confidence } \ge 0.65 \land \text{No AST Fallbacks} \implies \textbf{TARGETED SUITE}$$
- **Auditability:** Every decision records execution strategy, confidence scores, and plain-English explanation.

> **Speaker Notes:**
> "Phase 5 embodies the core safety policy specified in our approved synopsis. Even if AST maps an isolated module, if the Random Forest model predicts a failure risk of 70% or higher, optimization is aborted and the full suite is executed. If confidence is below 65%, full testing is enforced. Optimization only proceeds when failure risk is demonstrably low AND confidence is high."

---

### SLIDE 13: Full-Stack Architecture: API & Dashboard (Phases 6 & 7)
- **FastAPI REST Backend:** 11 production endpoints providing health, predictions, git churn, AST graphs, decisions, and telemetry.
- **SQLite Database Store:** Relational schema (`builds`, `predictions`, `decisions`, `build_files`, `build_tests`, `experiments`).
- **Interactive DevOps Dashboard:**
  - Built with responsive HTML5, modern CSS, and Chart.js.
  - 7 specialized tabs: Overview, AI Predictor, AST Dependency, Safety Engine, Live Runner, Model Benchmarks, Experiments.
  - Live console stream and real-time KPI updates.

> **Speaker Notes:**
> "In Phases 6 and 7, we built the complete backend and user interface. The FastAPI backend exposes 11 endpoints, backed by persistent SQLite storage. The frontend dashboard gives DevOps engineers complete visibility into model predictions, AST dependency links, live execution consoles, and empirical comparisons."

---

### SLIDE 14: DevOps Automation: GitHub Actions & Docker (Phase 8)
- **Conventional Baseline Workflow (`baseline.yml`):** Runs full regression test suite on push/PR, records duration and telemetry.
- **AI-Optimized Workflow (`ai-optimized.yml`):** Runs git churn analysis, ML prediction, AST test selection, safety gating, targeted test execution, and telemetry artifact archiving.
- **Production Dockerization:** Multi-stage `Dockerfile` (Python 3.11-slim) and `docker-compose.yml` with persistent volume mounting for SQLite and health checks.

> **Speaker Notes:**
> "Phase 8 provides real-world DevOps integration. We authored two independent GitHub Actions workflows—one baseline and one AI-optimized—running under identical runner environments. We also containerized the entire framework with Docker and Docker Compose."

---

### SLIDE 15: Automated Pytest Suite Verification (Phase 9)
- **Comprehensive Coverage:** 37 automated tests across 8 test modules.
- **Testing Scope:** Unit tests, integration tests, AST parser tests, test selector tests, safety engine rule tests, database tests, API tests, and end-to-end pipeline execution.
- **Verification Result:**
  $$\mathbf{37\text{ passed, } 0\text{ failed, } 0\text{ skipped in } 7.76\text{ seconds (100\% Pass Rate)}}$$

> **Speaker Notes:**
> "Phase 9 verifies software quality. We developed 37 automated pytest test cases covering every module, boundary condition, and safety fallback. The entire suite executes and passes 100% in under 8 seconds."

---

### SLIDE 16: Empirical Experimental Validation (Phase 10)
- **10 Controlled Commit Scenarios Evaluated:**
  - *SCEN-01:* Single Isolated Module (Inventory)
  - *SCEN-02:* Multi-Module Transitive (Auth $\to$ Payment): **53.33% Test Reduction**
  - *SCEN-03:* High-Risk Complex Churn: Safety Rule 1 Triggered (Full Suite Enforced)
  - *SCEN-04:* Non-Code Config Change: AST Fallback Triggered (Full Suite Enforced)
  - *SCEN-05:* Syntax Error Injection: Defect Detected by Both Baseline & Optimized (**100% Concordance**)
  - *SCEN-06:* Low-Confidence Churn: **63.33% Test Reduction**
  - *SCEN-07:* Targeted Defect Injection: Injected mutation caught by both pipelines (**100% Concordance**)
  - *SCEN-08:* Shared Core Utility Change: Broad AST propagation (Full Suite Enforced)
- **Aggregate Summary:** Up to **63.33% test reduction**, **100% Defect Retention Rate (Zero Escaped Bugs)**.

> **Speaker Notes:**
> "This is the most critical scientific validation of our project. We did not merely show model accuracy; we executed 10 real pipeline scenarios. In isolated and transitive changes, we achieved 53% to 63% test reduction. In Scenario 7, we injected a deliberate defect: both baseline and AI-optimized pipelines caught the defect with 100% concordance. Zero defects escaped."

---

### SLIDE 17: Conclusion & Key Contributions
- **Complete End-to-End Working System:** From Git commit to ML prediction, AST analysis, safety gating, test execution, SQLite persistence, and dashboard visualization.
- **Balanced Optimization & Safety:** Proved that test churn can be reduced by over 50% while guaranteeing that defect escape is prevented through fail-safe rules.
- **Academic & Industry Defensibility:** Fulfills all objectives and technology choices of the DSCE MCA Major Project specification.

> **Speaker Notes:**
> "In conclusion, this project delivers a complete, reproducible, and tested AI-driven CI/CD optimization platform. We proved that predictive ML combined with static AST analysis and conservative safety rules can substantially cut CI/CD test execution while preserving complete software reliability."

---

### SLIDE 18: References & Q&A
- **Key References:**
  - M. Beller et al., "TravisTorrent: Synthesizing Travis CI and GitHub for empirical software engineering research," *MSR 2017*.
  - S. Elbaum et al., "Techniques for improving regression testing in continuous integration environments," *FSE 2014*.
  - A. E. Hassan, "Predicting faults using the complexity of code changes," *ICSE 2009*.
  - C. Macho et al., "Predicting build failures with machine learning," *Empirical Software Engineering 2018*.
- **Thank You!** Open for Questions & Demonstration.

> **Speaker Notes:**
> "I thank the examiners and faculty for their kind attention. I am now ready for the live demonstration and to answer your questions."
