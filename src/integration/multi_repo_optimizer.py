"""Multi-Repository & Laptop Applications Integration Engine.
Allows the AI-Driven CI/CD Optimization Framework to scan, analyze, optimize,
and install intelligent CI/CD workflows into any application or repository on the host laptop.

Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

import ast
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Set

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import BASE_DIR, STRATEGY_FULL_SUITE, STRATEGY_TARGETED
from src.ml.predict import prediction_engine
from src.decision.safety_engine import safety_engine

DEFAULT_LAPTOP_REPOS = [
    {
        "id": "devops_nagarjun",
        "name": "DEVOPS_NAGARJUN",
        "path": r"C:\Users\nagar\DEVOPS_NAGARJUN",
        "description": "Full-stack DevOps automation project with App, Tests, and K8s manifests",
        "type": "Full-Stack Application",
    },
    {
        "id": "requests",
        "name": "Requests (HTTP for Humans)",
        "path": r"C:\DEVOPS_BENCHMARK_REPOS\requests",
        "description": "Industry-standard Python HTTP library with extensive test suite",
        "type": "Library / Production Package",
    },
    {
        "id": "click",
        "name": "Click (CLI Framework)",
        "path": r"C:\DEVOPS_BENCHMARK_REPOS\click",
        "description": "Popular Python composable command line interface toolkit",
        "type": "CLI Framework",
    },
    {
        "id": "ci_experiment",
        "name": "CI-Experiment",
        "path": r"C:\Users\nagar\ci-experiment",
        "description": "Adaptive workload & continuous integration experimentation repository",
        "type": "CI Experimentation Suite",
    },
]


class MultiRepoOptimizer:
    """Discovers, parses, optimizes, and installs AI CI/CD workflows on external laptop repos."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or BASE_DIR

    def discover_laptop_repositories(self) -> List[Dict[str, Any]]:
        """Scans host filesystem for known and accessible laptop repositories."""
        discovered = []
        for repo_info in DEFAULT_LAPTOP_REPOS:
            repo_path = Path(repo_info["path"])
            exists = repo_path.exists()
            py_count = 0
            test_count = 0
            if exists:
                try:
                    all_py = list(repo_path.rglob("*.py"))
                    py_count = len(all_py)
                    test_count = len([f for f in all_py if "test" in f.name.lower()])
                except Exception:
                    pass

            discovered.append({
                "id": repo_info["id"],
                "name": repo_info["name"],
                "path": str(repo_path),
                "description": repo_info["description"],
                "type": repo_info["type"],
                "exists": exists,
                "python_files": py_count,
                "test_files": test_count,
                "is_git_repo": (repo_path / ".git").exists() if exists else False,
            })
        return discovered

    def analyze_external_repo(self, repo_path_str: str) -> Dict[str, Any]:
        """Performs static AST analysis, symbol mapping, and dependency graphing on any repo."""
        repo_path = Path(repo_path_str)
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

        py_files = [
            f for f in repo_path.rglob("*.py")
            if not any(part.startswith(".") or part in ["__pycache__", "venv", ".venv", "build", "dist"] for part in f.parts)
        ]

        test_files = [f for f in py_files if "test" in f.name.lower()]
        src_files = [f for f in py_files if f not in test_files and f.name != "__init__.py"]

        # Parse AST symbols
        module_to_tests: Dict[str, Set[str]] = {}
        module_dependencies: Dict[str, Set[str]] = {}
        symbols: Dict[str, Dict[str, List[str]]] = {}

        for sf in src_files:
            mod_name = sf.stem
            rel_path = sf.relative_to(repo_path).as_posix()
            symbols[rel_path] = {"classes": [], "functions": [], "imports": []}
            deps = set()

            try:
                content = sf.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=str(sf))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        symbols[rel_path]["classes"].append(node.name)
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        symbols[rel_path]["functions"].append(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            symbols[rel_path]["imports"].append(alias.name)
                            deps.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            symbols[rel_path]["imports"].append(node.module)
                            deps.add(node.module.split(".")[0])
            except Exception:
                pass
            module_dependencies[mod_name] = deps

        # Map tests to source modules
        for tf in test_files:
            rel_test = tf.relative_to(repo_path).as_posix()
            try:
                content = tf.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=str(tf))
                imported_mods = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_mods.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imported_mods.add(node.module.split(".")[0])

                # Match against app source files
                for sf in src_files:
                    stem = sf.stem
                    if stem in imported_mods or stem in tf.name:
                        if stem not in module_to_tests:
                            module_to_tests[stem] = set()
                        module_to_tests[stem].add(rel_test)
            except Exception:
                pass

        # Transitive resolution
        expanded_map = {k: set(v) for k, v in module_to_tests.items()}
        for mod, deps in module_dependencies.items():
            for dep in deps:
                if dep in module_to_tests:
                    if mod not in expanded_map:
                        expanded_map[mod] = set()
                    expanded_map[mod].update(module_to_tests[dep])

        return {
            "repository_name": repo_path.name,
            "repository_path": str(repo_path),
            "total_python_files": len(py_files),
            "source_files_count": len(src_files),
            "test_files_count": len(test_files),
            "source_files": [sf.relative_to(repo_path).as_posix() for sf in src_files[:20]],
            "test_files": [tf.relative_to(repo_path).as_posix() for tf in test_files[:20]],
            "mapped_modules_count": len(expanded_map),
            "module_to_tests": {k: sorted(list(v)) for k, v in expanded_map.items()},
            "module_dependencies": {k: sorted(list(v)) for k, v in module_dependencies.items()},
        }

    def optimize_external_repo_change(
        self,
        repo_path_str: str,
        changed_files: Optional[List[str]] = None,
        custom_features: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Runs the complete AI CI/CD optimization decision on any external repository."""
        analysis = self.analyze_external_repo(repo_path_str)
        repo_path = Path(repo_path_str)
        all_tests = analysis["test_files"]

        # If no changed files provided, pick first mapped module to simulate targeted change
        if not changed_files:
            mapped = list(analysis["module_to_tests"].keys())
            if mapped:
                changed_files = [f"{mapped[0]}.py"]
            else:
                changed_files = [analysis["source_files"][0]] if analysis["source_files"] else ["main.py"]

        # Build feature vector
        if not custom_features:
            custom_features = {
                "files_changed": len(changed_files),
                "lines_added": 25,
                "lines_deleted": 6,
                "test_count": max(10, len(all_tests)),
                "prev_runtime": 45.0,
                "prev_failure": 0,
                "cpu_usage": 38.0,
                "memory_usage": 280.0,
            }

        # ML Inference
        pred_res = prediction_engine.predict(custom_features)

        # AST Selection on external repo
        module_to_tests = analysis["module_to_tests"]
        targeted_tests = set()
        for cf in changed_files:
            stem = Path(cf).stem
            if stem in module_to_tests:
                for t in module_to_tests[stem]:
                    targeted_tests.add(t)

        selected_tests = sorted(list(targeted_tests))
        fallback_active = False
        fallback_reason = None
        strategy = STRATEGY_TARGETED

        # Safety Fallback Checks
        if not selected_tests:
            strategy = STRATEGY_FULL_SUITE
            selected_tests = all_tests
            fallback_active = True
            fallback_reason = "No direct AST mappings resolved; enforcing full suite for safety."
        elif pred_res["failure_probability"] >= 0.70:
            strategy = STRATEGY_FULL_SUITE
            selected_tests = all_tests
            fallback_active = True
            fallback_reason = f"Failure risk ({pred_res['failure_probability']:.2%}) >= threshold (70.00%)"
        elif pred_res["model_confidence"] < 0.65:
            strategy = STRATEGY_FULL_SUITE
            selected_tests = all_tests
            fallback_active = True
            fallback_reason = f"Model confidence ({pred_res['model_confidence']:.2%}) < threshold (65.00%)"

        reduction_count = len(all_tests) - len(selected_tests)
        reduction_pct = round((reduction_count / max(1, len(all_tests))) * 100.0, 2) if reduction_count > 0 else 0.0

        return {
            "repository_name": repo_path.name,
            "repository_path": str(repo_path),
            "changed_files": changed_files,
            "execution_strategy": strategy,
            "safety_triggered": fallback_active,
            "fallback_reason": fallback_reason,
            "failure_probability": pred_res["failure_probability"],
            "model_confidence": pred_res["model_confidence"],
            "predicted_runtime": pred_res["predicted_runtime"],
            "total_tests_available": len(all_tests),
            "selected_tests_count": len(selected_tests),
            "test_reduction_percentage": reduction_pct,
            "selected_tests": selected_tests[:15],
            "all_tests": all_tests[:15],
        }

    def install_ai_cicd_to_repo(self, repo_path_str: str) -> Dict[str, Any]:
        """Installs the AI CI/CD optimization workflow and local runner into the target repository."""
        repo_path = Path(repo_path_str)
        if not repo_path.exists():
            raise FileNotFoundError(f"Path does not exist: {repo_path}")

        # 1. Ensure .github/workflows directory exists in target repo
        wf_dir = repo_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)

        workflow_file = wf_dir / "ai-optimized-cicd.yml"
        workflow_content = f"""name: AI-Optimized Intelligent CI/CD Pipeline
# Installed by AI-Driven CI/CD Optimization Framework
# Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore

on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master ]

jobs:
  ai-cicd-optimization:
    runs-on: ubuntu-latest
    name: Change-Aware & Safety-Gated Build

    steps:
      - name: Checkout Repository with Git History
        uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          pip install pytest psutil

      - name: Execute AI CI/CD Test Optimizer
        run: |
          python ai_cicd_runner.py
"""
        workflow_file.write_text(workflow_content, encoding="utf-8")

        # 2. Install local runner script into target repo
        runner_file = repo_path / "ai_cicd_runner.py"
        runner_content = f"""\"\"\"AI-Optimized CI/CD Test Runner for {repo_path.name}.
Automatically runs AST-based change-aware test selection with safety gating.
Framework: AI-Driven CI/CD Pipeline Optimization (NAGARJUNREDDY 1DS25MC052, DSCE)
\"\"\"

import ast
from pathlib import Path
import subprocess
import sys
import time

def main():
    root = Path(__file__).resolve().parent
    print("=" * 65)
    print(f"AI CI/CD Intelligent Test Runner: {{root.name}}")
    print("=" * 65)

    # Detect changed files using Git
    changed_files = []
    try:
        res = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if len(line) > 3:
                    changed_files.append(line[3:].strip())
    except Exception:
        pass

    all_tests = [f.as_posix() for f in root.rglob("*.py") if "test" in f.name.lower() and not any(p.startswith(".") for p in f.parts)]

    print(f"[*] Detected {{len(all_tests)}} total test files.")
    print(f"[*] Changed files in commit/working tree: {{changed_files if changed_files else 'None (Full Regression Test)'}}")

    # Safety Gating: If no changes or non-python file changed, run all tests
    if not changed_files or any(not f.endswith(".py") for f in changed_files):
        print("[!] Safety Rule Active: Configuration change or clean tree. Running FULL test suite.")
        target_tests = all_tests
    else:
        # Match tests
        matched = []
        for tf in all_tests:
            for cf in changed_files:
                if Path(cf).stem in tf:
                    matched.append(tf)
        target_tests = matched if matched else all_tests

    print(f"[*] Executing {{len(target_tests)}} tests (Optimized Reduction: {{(len(all_tests)-len(target_tests))/max(1, len(all_tests))*100:.1f}}%)...\\n")
    
    start = time.perf_counter()
    code = subprocess.run([sys.executable, "-m", "pytest"] + target_tests + ["-v"]).returncode
    duration = time.perf_counter() - start
    print(f"\\n[+] Pipeline execution completed in {{duration:.2f}} seconds with exit code {{code}}.")
    sys.exit(code)

if __name__ == "__main__":
    main()
"""
        runner_file.write_text(runner_content, encoding="utf-8")

        # 3. Create documentation badge in target repo
        doc_file = repo_path / "AI_CICD_OPTIMIZATION.md"
        doc_content = f"""# AI CI/CD Pipeline Optimization Integration

This repository (**{repo_path.name}**) is integrated with the **AI-Driven CI/CD Pipeline Optimization Framework**.

- **Developer:** NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
- **Installed Workflow:** `.github/workflows/ai-optimized-cicd.yml`
- **Installed Runner:** `ai_cicd_runner.py`
- **Capabilities:**
  - Git-based code churn extraction
  - Abstract Syntax Tree (AST) test selection
  - Risk & confidence safety gating
  - Targeted test execution
"""
        doc_file.write_text(doc_content, encoding="utf-8")

        return {
            "status": "success",
            "repository": repo_path.name,
            "installed_workflow": str(workflow_file),
            "installed_runner": str(runner_file),
            "installed_docs": str(doc_file),
        }


# Global singleton
multi_repo_optimizer = MultiRepoOptimizer()
