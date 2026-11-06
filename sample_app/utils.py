"""Sample Application: Shared Utility Functions."""

import re
from typing import Any, Dict


def format_currency(amount: float, symbol: str = "$") -> str:
    """Formats float currency to 2 decimal places."""
    if amount < 0:
        return f"-{symbol}{abs(amount):.2f}"
    return f"{symbol}{amount:.2f}"


def sanitize_string(text: str) -> str:
    """Removes special unwanted characters from text."""
    if not isinstance(text, str):
        return ""
    return re.sub(r"[^\w\s-]", "", text).strip()


def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculates discounted price."""
    if price < 0 or discount_percent < 0:
        raise ValueError("Price and discount must be non-negative.")
    if discount_percent > 100:
        raise ValueError("Discount cannot exceed 100%.")
    return round(price * (1.0 - (discount_percent / 100.0)), 2)


def clamp(val: float, min_val: float, max_val: float) -> float:
    """Clamps a numerical value within bounds."""
    return max(min_val, min(val, max_val))
