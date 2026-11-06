"""Unit tests for change-aware test selector and fail-safe fallback logic."""

import pytest
from src.selector.test_selector import test_selector
from src.config import STRATEGY_FULL_SUITE, STRATEGY_TARGETED


def test_discover_all_tests():
    all_tests = test_selector.get_all_tests()
    assert len(all_tests) == 5
    assert "sample_tests/test_auth.py" in all_tests
    assert "sample_tests/test_payment.py" in all_tests


def test_select_targeted_tests():
    res = test_selector.select_tests(["sample_app/inventory.py"])
    assert res["strategy"] == STRATEGY_TARGETED
    assert res["fallback_active"] is False
    assert "sample_tests/test_inventory.py" in res["selected_tests"]
    assert res["test_reduction_percentage"] > 0.0


def test_fallback_on_non_python_file():
    res = test_selector.select_tests(["Dockerfile", "requirements.txt"])
    assert res["strategy"] == STRATEGY_FULL_SUITE
    assert res["fallback_active"] is True
    assert "Non-Python" in res["fallback_reason"]
    assert len(res["selected_tests"]) == len(res["all_tests"])


def test_fallback_on_empty_input():
    res = test_selector.select_tests([])
    assert res["strategy"] == STRATEGY_FULL_SUITE
    assert res["fallback_active"] is True
    assert len(res["selected_tests"]) == len(res["all_tests"])


def test_fallback_on_unmapped_source_file():
    orphan_file = test_selector.base_dir / "sample_app" / "orphan_feature.py"
    try:
        orphan_file.write_text("def orphan_func():\n    return 'no test maps here'\n", encoding="utf-8")
        res = test_selector.select_tests(["sample_app/orphan_feature.py"])
        assert res["strategy"] == STRATEGY_FULL_SUITE
        assert res["fallback_active"] is True
        assert "no registered test mappings" in res["fallback_reason"]
    finally:
        if orphan_file.exists():
            orphan_file.unlink()
