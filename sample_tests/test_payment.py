"""Test suite for sample_app.payment module."""

import pytest
from sample_app.auth import AuthService
from sample_app.payment import PaymentProcessor


@pytest.fixture
def setup_payment():
    auth = AuthService()
    auth.register("alice", "password123")
    token = auth.authenticate("alice", "password123")
    processor = PaymentProcessor(auth)
    return processor, token


def test_process_valid_payment(setup_payment):
    processor, token = setup_payment
    res = processor.process_payment(token, 150.0)
    assert res["status"] == "COMPLETED"
    assert res["amount"] == 150.0
    assert res["formatted_amount"] == "$150.00"


def test_process_payment_invalid_token(setup_payment):
    processor, _ = setup_payment
    with pytest.raises(PermissionError):
        processor.process_payment("invalid_token", 50.0)


def test_process_payment_clamping(setup_payment):
    processor, token = setup_payment
    res_min = processor.process_payment(token, 0.05)
    assert res_min["amount"] == 0.50
    res_max = processor.process_payment(token, 999999.0)
    assert res_max["amount"] == 50000.0


def test_refund_successful(setup_payment):
    processor, token = setup_payment
    payment = processor.process_payment(token, 75.0)
    refund = processor.refund_payment(token, payment["txn_id"])
    assert refund["refund_status"] == "SUCCESS"


def test_refund_duplicate_fails(setup_payment):
    processor, token = setup_payment
    payment = processor.process_payment(token, 75.0)
    processor.refund_payment(token, payment["txn_id"])
    with pytest.raises(ValueError):
        processor.refund_payment(token, payment["txn_id"])


def test_refund_nonexistent_transaction(setup_payment):
    processor, token = setup_payment
    with pytest.raises(KeyError):
        processor.refund_payment(token, "TXN-99999")
