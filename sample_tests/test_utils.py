"""Test suite for sample_app.utils module."""

import pytest
from sample_app.utils import clamp, calculate_discount, format_currency, sanitize_string


def test_format_currency_positive():
    assert format_currency(12.5) == "$12.50"
    assert format_currency(100.0, "EUR ") == "EUR 100.00"


def test_format_currency_negative():
    assert format_currency(-45.99) == "-$45.99"


def test_sanitize_string():
    assert sanitize_string("Hello, World! <script>") == "Hello World script"
    assert sanitize_string("Normal-Text_123") == "Normal-Text_123"
    assert sanitize_string(12345) == ""


def test_calculate_discount_valid():
    assert calculate_discount(100.0, 20.0) == 80.0
    assert calculate_discount(50.0, 0.0) == 50.0
    assert calculate_discount(200.0, 100.0) == 0.0


def test_calculate_discount_invalid_percent():
    with pytest.raises(ValueError):
        calculate_discount(100.0, 150.0)


def test_calculate_discount_negative():
    with pytest.raises(ValueError):
        calculate_discount(-10.0, 10.0)


def test_clamp_within_bounds():
    assert clamp(5.0, 1.0, 10.0) == 5.0
    assert clamp(0.5, 1.0, 10.0) == 1.0
    assert clamp(25.0, 1.0, 10.0) == 10.0
