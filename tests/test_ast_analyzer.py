"""Unit tests for AST static code parser and dependency mapping."""

from pathlib import Path
import pytest
from src.analyzer.ast_parser import ast_analyzer


def test_parse_valid_python_file():
    target = Path("sample_app/auth.py")
    res = ast_analyzer.parse_python_file(target)
    assert res["valid"] is True
    assert "AuthService" in res["classes"]
    assert "register" in res["functions"]
    assert "authenticate" in res["functions"]
    assert "hashlib" in res["imports"]
    assert res["syntax_error"] is None


def test_parse_syntax_error_handling(tmp_path):
    bad_code = "def broken_syntax(:\n    return 42"
    bad_file = tmp_path / "broken.py"
    bad_file.write_text(bad_code, encoding="utf-8")

    res = ast_analyzer.parse_python_file(bad_file)
    assert res["valid"] is False
    assert res["syntax_error"] is not None
    assert "SyntaxError" in res["syntax_error"]


def test_build_test_dependency_map():
    dep_map = ast_analyzer.build_test_dependency_map(
        app_dir="sample_app", tests_dir="sample_tests"
    )
    assert "module_to_tests" in dep_map
    assert "test_to_modules" in dep_map

    m_to_t = dep_map["module_to_tests"]
    assert "auth" in m_to_t
    assert "sample_tests/test_auth.py" in m_to_t["auth"]
    assert "inventory" in m_to_t
    assert "sample_tests/test_inventory.py" in m_to_t["inventory"]


def test_transitive_dependency_resolution():
    dep_map = ast_analyzer.build_test_dependency_map(
        app_dir="sample_app", tests_dir="sample_tests"
    )
    # payment.py imports auth.py; therefore tests for payment should be mapped when auth changes
    auth_tests = dep_map["module_to_tests"]["auth"]
    assert "sample_tests/test_auth.py" in auth_tests
    assert "sample_tests/test_payment.py" in auth_tests
