"""AST-Based Source Code Dependency Analyzer.
Parses Python modules into Abstract Syntax Trees, extracts classes, functions,
imports, and establishes precise dependencies between source code and test files.

Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

import ast
from pathlib import Path
import sys
from typing import Dict, List, Optional, Set

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import BASE_DIR


class ASTDependencyAnalyzer:
    """Extracts structural entities and maps test dependencies using Python's AST."""

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or BASE_DIR

    def parse_python_file(self, file_path: Path) -> Dict[str, any]:
        """Parses a Python file into an AST and extracts defined symbols and imports.
        Returns error indicator if file contains invalid syntax.
        """
        full_path = self.root_dir / file_path if not file_path.is_absolute() else file_path
        
        result = {
            "file": str(file_path).replace("\\", "/"),
            "valid": False,
            "classes": [],
            "functions": [],
            "imports": [],
            "calls": [],
            "syntax_error": None,
        }

        if not full_path.exists():
            result["syntax_error"] = f"File does not exist: {full_path}"
            return result

        try:
            source = full_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(full_path))
            result["valid"] = True

            for node in ast.walk(tree):
                # 1. Classes
                if isinstance(node, ast.ClassDef):
                    result["classes"].append(node.name)
                
                # 2. Functions and Methods
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    result["functions"].append(node.name)

                # 3. Direct imports: import foo, import foo.bar as b
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        result["imports"].append(alias.name)

                # 4. From imports: from foo import bar
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    for alias in node.names:
                        result["imports"].append(f"{mod}.{alias.name}" if mod else alias.name)
                        if mod and mod not in result["imports"]:
                            result["imports"].append(mod)

                # 5. Calls: func()
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        result["calls"].append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        result["calls"].append(node.func.attr)

            # Deduplicate symbols
            result["classes"] = sorted(list(set(result["classes"])))
            result["functions"] = sorted(list(set(result["functions"])))
            result["imports"] = sorted(list(set(result["imports"])))
            result["calls"] = sorted(list(set(result["calls"])))

            return result

        except SyntaxError as se:
            result["valid"] = False
            result["syntax_error"] = f"SyntaxError at line {se.lineno}: {se.msg}"
            return result
        except Exception as e:
            result["valid"] = False
            result["syntax_error"] = f"Parse exception: {str(e)}"
            return result

    def build_test_dependency_map(
        self,
        app_dir: str = "sample_app",
        tests_dir: str = "sample_tests",
    ) -> Dict[str, any]:
        """Scans the test directory and builds a mapping from application modules to test files."""
        tests_path = self.root_dir / tests_dir
        app_path = self.root_dir / app_dir

        module_to_tests: Dict[str, Set[str]] = {}
        test_to_modules: Dict[str, Set[str]] = {}
        module_dependencies: Dict[str, Set[str]] = {}
        parse_errors: Dict[str, str] = {}

        # 1. Analyze inter-module dependencies within application code
        if app_path.exists():
            for py_file in app_path.glob("**/*.py"):
                if py_file.name == "__init__.py":
                    continue
                mod_name = py_file.stem
                rel_path = py_file.relative_to(self.root_dir).as_posix()
                parsed = self.parse_python_file(py_file)
                
                if not parsed["valid"]:
                    parse_errors[rel_path] = parsed["syntax_error"]
                    continue

                deps = set()
                for imp in parsed["imports"]:
                    # Match against other application modules
                    for other_file in app_path.glob("**/*.py"):
                        if other_file.stem != mod_name and (
                            other_file.stem in imp or f"{app_dir}.{other_file.stem}" in imp
                        ):
                            deps.add(other_file.stem)
                module_dependencies[mod_name] = deps

        # 2. Analyze test dependencies on application modules
        if tests_path.exists():
            for test_file in tests_path.glob("**/*.py"):
                if test_file.name == "__init__.py":
                    continue
                test_rel_path = test_file.relative_to(self.root_dir).as_posix()
                parsed_test = self.parse_python_file(test_file)

                if not parsed_test["valid"]:
                    parse_errors[test_rel_path] = parsed_test["syntax_error"]
                    continue

                referenced_modules = set()
                for imp in parsed_test["imports"]:
                    # Check which app modules are imported in this test file
                    if app_path.exists():
                        for app_file in app_path.glob("**/*.py"):
                            app_mod = app_file.stem
                            if app_mod in imp or f"{app_dir}.{app_mod}" in imp:
                                referenced_modules.add(app_mod)

                test_to_modules[test_rel_path] = referenced_modules

                for app_mod in referenced_modules:
                    if app_mod not in module_to_tests:
                        module_to_tests[app_mod] = set()
                    module_to_tests[app_mod].add(test_rel_path)

        # 3. Transitive dependency resolution:
        # If payment depends on auth and utils, changes to utils should also trigger payment tests!
        expanded_module_to_tests: Dict[str, Set[str]] = {
            m: set(ts) for m, ts in module_to_tests.items()
        }
        for base_mod, dependent_mods in module_dependencies.items():
            # If dependent_mods depend on base_mod, their tests should also test base_mod
            for dep in dependent_mods:
                if dep in module_to_tests:
                    if base_mod not in expanded_module_to_tests:
                        expanded_module_to_tests[base_mod] = set()
                    expanded_module_to_tests[base_mod].update(module_to_tests[dep])

        return {
            "module_to_tests": {k: sorted(list(v)) for k, v in expanded_module_to_tests.items()},
            "direct_module_to_tests": {k: sorted(list(v)) for k, v in module_to_tests.items()},
            "test_to_modules": {k: sorted(list(v)) for k, v in test_to_modules.items()},
            "module_dependencies": {k: sorted(list(v)) for k, v in module_dependencies.items()},
            "parse_errors": parse_errors,
        }


# Global singleton
ast_analyzer = ASTDependencyAnalyzer()
