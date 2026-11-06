# LIVE DEMONSTRATION & PRACTICAL PRESENTATION SCRIPT
## AI-DRIVEN CI/CD PIPELINE OPTIMIZATION

**Student Name:** NAGARJUNREDDY (1DS25MC052)  
**Supervisor:** Prof. Mahendra Kumar B  
**Department:** Master of Computer Applications, Dayananda Sagar College of Engineering  

---

## 1. Demonstration Environment Preparation

Open a terminal (PowerShell) in the workspace directory `C:\PRO_1DS25MC052`.

Verify Python, Git, and dependencies:
```powershell
python --version
git --version
python -c "import sklearn, pandas, numpy, fastapi, uvicorn, pytest; print('All core libraries verified!')"
```

---

## 2. Step-by-Step Demonstration Sequence

### Step 1: Start the Backend & Monitoring Dashboard
Execute:
```powershell
uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```
Open your web browser and navigate to:
`http://127.0.0.1:8000`

**Key Points to Show External Examiner:**
- Highlight the **System Health Badge** in the top right (`● System Healthy - Models & DB Active`).
- Show the 7 dedicated tabs: Overview & Telemetry, AI Risk & Runtime, AST Code Dependency, Safety Decision Engine, Live Pipeline Runner, ML Benchmarks, Empirical Experiments.
- Show the active KPI cards reading live execution stats from SQLite.

---

### Step 2: Demonstrate ML Model Benchmarks
Click on the **ML Model Benchmarks** tab in the dashboard.

**Key Points to Show:**
- Explain the benchmark bar chart comparing **Logistic Regression**, **Decision Tree**, and **Random Forest**.
- Emphasize why **Random Forest** was chosen as champion: Failure Recall = 74.12%, F1-Score = 0.5248.
- Explain the regression benchmark: Linear Regression achieved an MAE of 5.31 seconds compared to the 26.56s baseline error.

---

### Step 3: Demonstrate AST Dependency Graph
Click on the **AST Code Dependency** tab.

**Key Points to Show:**
- Show the direct and transitive mapping tree:
  - `sample_app/inventory.py` ➔ mapped to `test_inventory.py` and `test_utils.py`.
  - `sample_app/auth.py` ➔ mapped to `test_auth.py` and `test_payment.py` (transitive relationship!).
  - `sample_app/utils.py` ➔ core utility affecting all modules.

---

### Step 4: Demonstrate Interactive AI Prediction & Safety Gating
Click on the **AI Risk & Runtime Prediction** tab.

**Action A: Test Targeted Test Approval**
- Target File: `sample_app/inventory.py`
- Files Changed: 1, Lines Added: 10, Lines Deleted: 2
- Test Count: 30, Prev Runtime: 35.0, Prev Failure: 0
- CPU Usage: 30%, Memory: 210 MB
- Click **Run AI Inference & Safety Evaluation**.
- **Expected Result:**
  - Failure Risk: Low (< 25%)
  - Strategy Badge: `TARGETED` (Green)
  - Selected Tests: only 2 test files selected out of 5!

**Action B: Test High-Risk Safety Threshold Gating ($\ge 0.70$)**
- Change Lines Added to 350, Lines Deleted to 150, Prev Failure: 1.
- Click **Run AI Inference & Safety Evaluation**.
- **Expected Result:**
  - Failure Risk increases.
  - If Risk $\ge 70\%$ or Confidence $< 65\%$, Strategy Badge immediately changes to `FULL_TEST_SUITE` (Red) with formal audit explanation.

**Action C: Test Non-Code AST Fallback**
- Select `requirements.txt` from the dropdown.
- Click **Run AI Inference**.
- **Expected Result:** Immediate fallback to `FULL_TEST_SUITE` with reason: *"Non-Python or configuration files modified. AST mapping cannot guarantee safe omission."*

---

### Step 5: Execute Real Pipeline Runs from the Dashboard
Click on the **Live Pipeline Runner** tab.

**Execution 1: Conventional Baseline Pipeline**
- Select Mode: `Conventional Baseline Pipeline (Full Suite)`.
- Click **🚀 Run Pipeline**.
- Observe live console output: Runs all 30 tests across all 5 test files. Shows duration, CPU %, and memory.
- Check that the Overview KPI table updates automatically!

**Execution 2: AI-Optimized Pipeline**
- Select Mode: `AI-Optimized Pipeline`, File: `sample_app/inventory.py`.
- Click **🚀 Run Pipeline**.
- Observe console output: Runs targeted tests, achieves test churn reduction, captures telemetry, and persists to SQLite.

---

### Step 6: Demonstrate Empirical Benchmark Results & Defect Retention
Click on the **Empirical Experiments** tab.

**Key Points to Show:**
- Present the 10 controlled scenarios.
- Highlight **Scenario 7 (Targeted Module Defect Injection)**:
  - Both Baseline and AI-Optimized caught the defect (`100% Retained`).
  - Proves that reducing tests did not allow any bugs to escape.

---

### Step 7: Demonstrate Automated Pytest Suite
In a second terminal window, run:
```powershell
python -m pytest tests -v
```
Show all 37 automated tests passing in ~7 seconds, covering unit, integration, AST parsing, ML inference, safety gating, and database operations.
