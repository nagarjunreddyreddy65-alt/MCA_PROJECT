"""Intelligent Change-Aware Test Selector.
Maps modified source code to targeted regression test suites with guaranteed
fail-safe fallback to the complete test suite.

Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

from pathlib import Path
import sys
from typing import Dict, List, Optional, Set

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import BASE_DIR, STRATEGY_FULL_SUITE, STRATEGY_TARGETED
from src.analyzer.ast_parser import ast_analyzer


class TestSelectionEngine:
    """Selects affected test cases based on AST dependency analysis."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or BASE_DIR
        self.tests_dir = "sample_tests"
        self.app_dir = "sample_app"

    def get_all_tests(self) -> List[str]:
        """Discovers all test files present in the test suite directory."""
        test_path = self.base_dir / self.tests_dir
        if not test_path.exists():
            return []
        test_files = [
            f.relative_to(self.base_dir).as_posix()
            for f in sorted(test_path.glob("**/test_*.py"))
        ]
        return test_files

    def select_tests(self, changed_files: List[str]) -> Dict[str, any]:
        """Selects the minimal sufficient test subset or falls back safely to full suite.

        Fallback triggers:
        1. Non-Python / configuration file modified.
        2. AST syntax or parsing error.
        3. Changed Python file has no mapped test.
        4. Empty targeted test set despite changes.
        5. Core structural module change.
        """
        all_tests = self.get_all_tests()
        if not all_tests:
            return {
                "strategy": STRATEGY_FULL_SUITE,
                "fallback_active": True,
                "fallback_reason": "No automated test files discovered in test suite directory.",
                "selected_tests": [],
                "all_tests": [],
                "total_tests_count": 0,
                "selected_tests_count": 0,
                "test_reduction_count": 0,
                "test_reduction_percentage": 0.0,
                "affected_modules": [],
            }

        # Normalize changed file paths
        normalized_changes = [p.replace("\\", "/").strip() for p in changed_files if p.strip()]

        if not normalized_changes:
            # If no files changed at all, fallback to full suite as a precaution
            return {
                "strategy": STRATEGY_FULL_SUITE,
                "fallback_active": True,
                "fallback_reason": "No changed files specified. Running baseline full test suite.",
                "selected_tests": all_tests,
                "all_tests": all_tests,
                "total_tests_count": len(all_tests),
                "selected_tests_count": len(all_tests),
                "test_reduction_count": 0,
                "test_reduction_percentage": 0.0,
                "affected_modules": [],
            }

        # Fallback Check 1: Non-Python or infrastructure configuration change
        non_python_files = [
            f for f in normalized_changes if not f.endswith(".py")
        ]
        if non_python_files:
            return {
                "strategy": STRATEGY_FULL_SUITE,
                "fallback_active": True,
                "fallback_reason": f"Non-Python or configuration files modified ({', '.join(non_python_files[:3])}). AST mapping cannot guarantee safe omission.",
                "selected_tests": all_tests,
                "all_tests": all_tests,
                "total_tests_count": len(all_tests),
                "selected_tests_count": len(all_tests),
                "test_reduction_count": 0,
                "test_reduction_percentage": 0.0,
                "affected_modules": [],
            }

        # Build AST Dependency Map
        dep_map = ast_analyzer.build_test_dependency_map(
            app_dir=self.app_dir, tests_dir=self.tests_dir
        )

        # Fallback Check 2: AST Parsing Error in changed files
        for f in normalized_changes:
            full_path = self.base_dir / f
            parsed = ast_analyzer.parse_python_file(full_path)
            if not parsed["valid"]:
                return {
                    "strategy": STRATEGY_FULL_SUITE,
                    "fallback_active": True,
                    "fallback_reason": f"AST Syntax/Parsing error in {f}: {parsed.get('syntax_error')}. Forcing full suite.",
                    "selected_tests": all_tests,
                    "all_tests": all_tests,
                    "total_tests_count": len(all_tests),
                    "selected_tests_count": len(all_tests),
                    "test_reduction_count": 0,
                    "test_reduction_percentage": 0.0,
                    "affected_modules": [],
                }

        # Check if modified files are direct test files
        modified_tests = [f for f in normalized_changes if f in all_tests]

        # Map modified application source files
        module_to_tests = dep_map["module_to_tests"]
        targeted_tests: Set[str] = set(modified_tests)
        affected_modules: List[str] = []

        for f in normalized_changes:
            stem = Path(f).stem
            if stem == "__init__":
                continue
            affected_modules.append(stem)

            if stem in module_to_tests:
                for t in module_to_tests[stem]:
                    targeted_tests.add(t)
            elif f not in all_tests:
                # Fallback Check 3: A source file was changed that has NO mapped test!
                return {
                    "strategy": STRATEGY_FULL_SUITE,
                    "fallback_active": True,
                    "fallback_reason": f"Modified source module '{stem}' has no registered test mappings in dependency graph. Forcing full suite.",
                    "selected_tests": all_tests,
                    "all_tests": all_tests,
                    "total_tests_count": len(all_tests),
                    "selected_tests_count": len(all_tests),
                    "test_reduction_count": 0,
                    "test_reduction_percentage": 0.0,
                    "affected_modules": affected_modules,
                }

        selected_list = sorted(list(targeted_tests))

        # Fallback Check 4: Empty test selection despite source code modification
        if not selected_list:
            return {
                "strategy": STRATEGY_FULL_SUITE,
                "fallback_active": True,
                "fallback_reason": "Targeted test resolution returned empty test set. Forcing full test suite for safety.",
                "selected_tests": all_tests,
                "all_tests": all_tests,
                "total_tests_count": len(all_tests),
                "selected_tests_count": len(all_tests),
                "test_reduction_count": 0,
                "test_reduction_percentage": 0.0,
                "affected_modules": affected_modules,
            }

        # If targeted selection happens to cover 100% of all tests, strategy is FULL_TEST_SUITE
        if len(selected_list) == len(all_tests):
            return {
                "strategy": STRATEGY_FULL_SUITE,
                "fallback_active": False,
                "fallback_reason": "Changes cross-cut all dependent application modules; full test suite required.",
                "selected_tests": all_tests,
                "all_tests": all_tests,
                "total_tests_count": len(all_tests),
                "selected_tests_count": len(all_tests),
                "test_reduction_count": 0,
                "test_reduction_percentage": 0.0,
                "affected_modules": affected_modules,
            }

        # Valid Targeted Selection
        reduction_count = len(all_tests) - len(selected_list)
        reduction_pct = round((reduction_count / len(all_tests)) * 100.0, 2)

        return {
            "strategy": STRATEGY_TARGETED,
            "fallback_active": False,
            "fallback_reason": None,
            "selected_tests": selected_list,
            "all_tests": all_tests,
            "total_tests_count": len(all_tests),
            "selected_tests_count": len(selected_list),
            "test_reduction_count": reduction_count,
            "test_reduction_percentage": reduction_pct,
            "affected_modules": affected_modules,
        }


# Global singleton
test_selector = TestSelectionEngine()
