"""Test suite for sample_app.notifications module."""

import pytest
from sample_app.notifications import NotificationService


@pytest.fixture
def notifier():
    return NotificationService()


def test_send_email_success(notifier):
    res = notifier.send_email("user@example.com", "Test Subject", "Hello World")
    assert res["status"] == "DELIVERED"
    assert res["channel"] == "EMAIL"
    assert res["recipient"] == "user@example.com"


def test_send_email_invalid_recipient(notifier):
    with pytest.raises(ValueError):
        notifier.send_email("invalid-address", "Subject", "Body")


def test_send_sms_success(notifier):
    res = notifier.send_sms("+1234567890", "Your code is 1234")
    assert res["status"] == "DELIVERED"
    assert res["channel"] == "SMS"


def test_send_sms_invalid_phone(notifier):
    with pytest.raises(ValueError):
        notifier.send_sms("123", "Too short")
