"""Sample Application: Inventory Management Service.
Depends on sample_app.utils.
"""

from typing import Dict
from sample_app.utils import clamp


class InventoryManager:
    def __init__(self):
        self.stock: Dict[str, int] = {}

    def add_product(self, product_id: str, quantity: int) -> int:
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        self.stock[product_id] = self.stock.get(product_id, 0) + quantity
        return self.stock[product_id]

    def reserve_stock(self, product_id: str, quantity: int) -> bool:
        if product_id not in self.stock or self.stock[product_id] < quantity:
            return False
        self.stock[product_id] -= quantity
        return True

    def get_stock(self, product_id: str) -> int:
        return self.stock.get(product_id, 0)
