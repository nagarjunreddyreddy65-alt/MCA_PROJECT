"""Sample Application: Payment Processing Module.
Depends on sample_app.auth and sample_app.utils.
"""

from typing import Dict, Optional
from sample_app.auth import AuthService
from sample_app.utils import format_currency, clamp


class PaymentProcessor:
    def __init__(self, auth_service: AuthService):
        self.auth = auth_service
        self.transactions: Dict[str, Dict] = {}

    def process_payment(self, token: str, amount: float, currency: str = "USD") -> Dict:
        username = self.auth.verify_token(token)
        if not username:
            raise PermissionError("Unauthorized payment: Invalid or expired auth token.")
        
        amount = clamp(amount, 0.50, 50000.0)
        txn_id = f"TXN-{len(self.transactions) + 1:05d}"
        
        record = {
            "txn_id": txn_id,
            "username": username,
            "amount": amount,
            "currency": currency,
            "formatted_amount": format_currency(amount),
            "status": "COMPLETED",
        }
        self.transactions[txn_id] = record
        return record

    def refund_payment(self, token: str, txn_id: str) -> Dict:
        username = self.auth.verify_token(token)
        if not username:
            raise PermissionError("Unauthorized refund attempt.")
        if txn_id not in self.transactions:
            raise KeyError(f"Transaction {txn_id} not found.")

        txn = self.transactions[txn_id]
        if txn["status"] == "REFUNDED":
            raise ValueError(f"Transaction {txn_id} already refunded.")

        txn["status"] = "REFUNDED"
        return {"txn_id": txn_id, "refund_status": "SUCCESS"}
