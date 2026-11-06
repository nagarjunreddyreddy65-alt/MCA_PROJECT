# COMPLETE TOOL INTEGRATION & DEVELOPER ENVIRONMENT GUIDE
## AI-DRIVEN CI/CD PIPELINE OPTIMIZATION

**Student Name:** NAGARJUNREDDY (1DS25MC052)  
**Supervisor:** Prof. Mahendra Kumar B  
**Department:** Master of Computer Applications, Dayananda Sagar College of Engineering  

---

## 1. Integrated Tool Ecosystem Overview

This project unifies modern software development, machine learning, testing, and DevOps automation tools into a cohesive developer experience:

```
[VS Code IDE]
     ↕
[Git Version Control] ─── Push ───> [GitHub Cloud Repository]
     ↕                                      ↕
[Local Pytest Suite]               [GitHub Actions CI/CD]
     ↕                                      ↕
[FastAPI & Uvicorn] ◄── Docker ──► [Docker Container]
     ↕
[SQLite Telemetry Store]
```

---

## 2. Visual Studio Code (VS Code) Integration

The workspace includes pre-configured settings in the `.vscode/` directory:

### 2.1 Debug & Run Configurations (`.vscode/launch.json`)
Press **F5** in VS Code to run any of the configured tasks:
1. `🚀 Launch FastAPI & Dashboard (Port 8000)`: Starts Uvicorn with hot-reload enabled.
2. `🧪 Run All Pytest Tests`: Runs the 37 automated tests with verbose output in the terminal.
3. `🔬 Run Controlled Experiments`: Executes the 10 empirical benchmark scenarios.
4. `🧠 Retrain All ML Models`: Executes `src/ml/train_all.py` to recompute model weights.
5. `⚡ Run AI-Optimized Pipeline`: Runs live change detection and pipeline simulation.

### 2.2 Build Tasks (`.vscode/tasks.json`)
Press **Ctrl + Shift + B** in VS Code to trigger default build tasks:
- `🚀 Start FastAPI Server & Dashboard` (Default Build Task)
- `🧪 Run Pytest Test Suite` (Default Test Task)
- `🐳 Docker Compose Build & Up`
- `📊 Generate Report & Slide PDFs`

### 2.3 Recommended Extensions (`.vscode/extensions.json`)
VS Code prompts to install recommended extensions:
- Python (`ms-python.python`)
- Pylance (`ms-python.vscode-pylance`)
- Debugpy (`ms-python.debugpy`)
- Docker (`ms-azuretools.vscode-docker`)
- GitLens (`eamodio.gitlens`)
- SQLite Viewer (`qwtel.sqlite-viewer`): Inspect `cicd_telemetry.db` directly inside VS Code!

---

## 3. Git Version Control Integration

The workspace is a fully initialized Git repository on the `main` branch:
- **Author Identity:** `NAGARJUNREDDY <1ds25mc052@dsce.edu.in>`
- **Active Git Churn Analyzer:** `src/analyzer/git_diff.py` interacts directly with Git:
  - Reads `git status --porcelain` to identify added, modified, or deleted files.
  - Reads `git diff --numstat` to compute exact line churn (insertions/deletions).
  - Supplies live churn metrics to the ML risk prediction engine.

---

## 4. GitHub & GitHub Actions Cloud Integration

### 4.1 How to Connect to a New GitHub Repository
1. Log in to your GitHub account: [https://github.com/new](https://github.com/new)
2. Create a new repository named: `AI-Driven-CICD-Pipeline-Optimization`
   *(Important: Do NOT check "Add a README file", ".gitignore", or "license")*
3. Run the automated script:
   - **On Windows (Double-click or PowerShell):**
     ```powershell
     .\scripts\setup_github.bat
     # OR
     .\scripts\setup_github.ps1
     ```
   - Enter your repository URL (e.g., `https://github.com/YOUR_USERNAME/AI-Driven-CICD-Pipeline-Optimization.git`).
4. The script will automatically link the remote and push the entire commit history!

### 4.2 GitHub Actions Automated Workflows
Once pushed to GitHub, two workflows execute automatically under the **Actions** tab:
1. **Conventional Baseline Workflow (`.github/workflows/baseline.yml`):**
   - Provisions Ubuntu runner with Python 3.11.
   - Executes the full 30-test suite across all modules.
   - Records execution time and archives telemetry.
2. **AI-Optimized Workflow (`.github/workflows/ai-optimized.yml`):**
   - Checks out repository with full commit history.
   - Extracts churn features and runs Random Forest failure risk prediction.
   - Analyzes AST dependencies to find affected tests.
   - Enforces safety rules ($P \ge 0.70$ or Confidence $< 0.65$).
   - Executes targeted tests and uploads SQLite telemetry artifacts.

---

## 5. Docker Containerization Integration

### 5.1 Dockerfile Architecture
The multi-stage `Dockerfile` packages:
- Python 3.11 slim runtime.
- System tools: `git` and `curl`.
- All Python requirements from `requirements.txt`.
- Trained ML models, application code, test suites, and the web dashboard.
- Active health check at `/api/health`.

### 5.2 1-Click Execution via Docker Compose
To run in Docker:
```powershell
.\scripts\docker_build_run.bat
# OR
docker compose up --build
```
Access the application at `http://localhost:8000`. The container mounts `./cicd_telemetry.db` as a persistent volume, ensuring data survives container restarts.

---

## 6. One-Click Convenience Scripts (`scripts/`)

| Script | Purpose |
|---|---|
| `scripts/run_app.bat` / `.ps1` | Starts FastAPI & automatically opens browser dashboard at `http://127.0.0.1:8000` |
| `scripts/run_tests.bat` / `.ps1` | Runs 37 automated verification tests via Pytest |
| `scripts/run_experiments.bat` / `.ps1` | Executes the 10 controlled empirical benchmark scenarios |
| `scripts/setup_github.bat` / `.ps1` | Connects local Git repository to GitHub and pushes `main` |
| `scripts/docker_build_run.bat` / `.ps1` | Builds and launches Docker container |
| `scripts/query_telemetry.py` | Command-line CLI tool to inspect SQLite telemetry records |
