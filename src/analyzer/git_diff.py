"""Git Change Detection & Churn Analyzer.
Inspects the repository's version control status to identify added, modified,
and deleted files and calculates code churn metrics (lines added/deleted).

Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

from pathlib import Path
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import BASE_DIR


class GitDiffAnalyzer:
    """Detects file modifications and computes churn from the active git repository."""

    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path or BASE_DIR

    def _run_git(self, args: List[str]) -> Tuple[int, str, str]:
        """Runs a git command inside the repository directory."""
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            return res.returncode, res.stdout.strip(), res.stderr.strip()
        except Exception as e:
            return 1, "", str(e)

    def get_changed_files(self, base_commit: Optional[str] = None) -> Dict[str, List[str]]:
        """Identifies added, modified, deleted, and untracked files.
        If base_commit is provided, diffs against that commit; otherwise against HEAD + working tree.
        """
        changes = {
            "added": [],
            "modified": [],
            "deleted": [],
            "all_changed": [],
            "python_files": [],
            "non_python_files": [],
        }

        # Check working tree status
        code, out, _ = self._run_git(["status", "--porcelain"])
        if code == 0 and out:
            for line in out.splitlines():
                if len(line) < 3:
                    continue
                status_code = line[:2].strip()
                file_path = line[3:].strip().replace('"', "")

                if status_code in ["M", "MM", "AM"]:
                    changes["modified"].append(file_path)
                elif status_code in ["A", "??"]:
                    changes["added"].append(file_path)
                elif status_code in ["D"]:
                    changes["deleted"].append(file_path)

        # If base_commit is specified or comparing commit to HEAD~1
        if base_commit:
            diff_cmd = ["diff", "--name-status", base_commit]
            code, out, _ = self._run_git(diff_cmd)
            if code == 0 and out:
                for line in out.splitlines():
                    parts = line.split(maxsplit=1)
                    if len(parts) == 2:
                        s_code, f_path = parts[0], parts[1].strip()
                        if s_code.startswith("A") and f_path not in changes["added"]:
                            changes["added"].append(f_path)
                        elif s_code.startswith("M") and f_path not in changes["modified"]:
                            changes["modified"].append(f_path)
                        elif s_code.startswith("D") and f_path not in changes["deleted"]:
                            changes["deleted"].append(f_path)

        # Aggregate unique changed paths
        all_unique = sorted(list(set(changes["added"] + changes["modified"] + changes["deleted"])))
        changes["all_changed"] = all_unique

        for p in all_unique:
            if p.endswith(".py"):
                changes["python_files"].append(p)
            else:
                changes["non_python_files"].append(p)

        return changes

    def get_churn_metrics(self, base_commit: Optional[str] = None) -> Dict[str, int]:
        """Calculates line additions and deletions across all modified files."""
        lines_added = 0
        lines_deleted = 0

        # Diff working tree
        args = ["diff", "--numstat"]
        if base_commit:
            args.append(base_commit)

        code, out, _ = self._run_git(args)
        if code == 0 and out:
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        add_str, del_str = parts[0], parts[1]
                        if add_str != "-":
                            lines_added += int(add_str)
                        if del_str != "-":
                            lines_deleted += int(del_str)
                    except ValueError:
                        continue

        # Also count lines in untracked files
        status_code, status_out, _ = self._run_git(["status", "--porcelain"])
        if status_code == 0 and status_out:
            for s_line in status_out.splitlines():
                if s_line.startswith("??"):
                    untracked_file = self.repo_path / s_line[3:].strip().replace('"', "")
                    if untracked_file.is_file():
                        try:
                            lines_added += sum(1 for _ in untracked_file.open(encoding="utf-8", errors="ignore"))
                        except Exception:
                            pass

        return {
            "lines_added": max(0, lines_added),
            "lines_deleted": max(0, lines_deleted),
            "total_churn": max(0, lines_added + lines_deleted),
        }

    def extract_git_features(
        self,
        test_count: int = 30,
        prev_runtime: float = 45.0,
        prev_failure: int = 0,
        cpu_usage: float = 40.0,
        memory_usage: float = 300.0,
    ) -> Dict[str, any]:
        """Extracts complete feature dictionary directly from the live git workspace."""
        changes = self.get_changed_files()
        churn = self.get_churn_metrics()

        files_changed_count = max(1, len(changes["all_changed"]))

        features = {
            "files_changed": files_changed_count,
            "lines_added": churn["lines_added"],
            "lines_deleted": churn["lines_deleted"],
            "test_count": test_count,
            "prev_runtime": prev_runtime,
            "prev_failure": prev_failure,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
        }
        return {
            "features": features,
            "changed_files_detail": changes,
            "churn_detail": churn,
        }


# Global singleton
git_analyzer = GitDiffAnalyzer()
