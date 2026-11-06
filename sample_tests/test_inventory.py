"""Test suite for sample_app.inventory module."""

import pytest
from sample_app.inventory import InventoryManager


@pytest.fixture
def inventory():
    inv = InventoryManager()
    inv.add_product("PROD-1", 100)
    inv.add_product("PROD-2", 50)
    return inv


def test_initial_stock(inventory):
    assert inventory.get_stock("PROD-1") == 100
    assert inventory.get_stock("PROD-2") == 50
    assert inventory.get_stock("PROD-UNKNOWN") == 0


def test_add_stock_valid(inventory):
    total = inventory.add_product("PROD-1", 25)
    assert total == 125
    assert inventory.get_stock("PROD-1") == 125


def test_add_stock_negative_fails(inventory):
    with pytest.raises(ValueError):
        inventory.add_product("PROD-1", -10)


def test_reserve_stock_sufficient(inventory):
    success = inventory.reserve_stock("PROD-1", 30)
    assert success is True
    assert inventory.get_stock("PROD-1") == 70


def test_reserve_stock_insufficient(inventory):
    success = inventory.reserve_stock("PROD-2", 60)
    assert success is False
    assert inventory.get_stock("PROD-2") == 50
