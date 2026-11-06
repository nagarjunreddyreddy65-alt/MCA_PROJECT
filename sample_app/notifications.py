"""Sample Application: Notification Dispatcher Service.
Depends on sample_app.utils.
"""

from typing import Dict, List
from sample_app.utils import sanitize_string


class NotificationService:
    def __init__(self):
        self.sent_messages: List[Dict] = []

    def send_email(self, recipient: str, subject: str, body: str) -> Dict:
        if "@" not in recipient:
            raise ValueError(f"Invalid email recipient: {recipient}")
        
        record = {
            "channel": "EMAIL",
            "recipient": recipient,
            "subject": sanitize_string(subject),
            "body": body,
            "status": "DELIVERED",
        }
        self.sent_messages.append(record)
        return record

    def send_sms(self, phone: str, message: str) -> Dict:
        if len(phone) < 7:
            raise ValueError(f"Invalid phone number: {phone}")
        record = {
            "channel": "SMS",
            "recipient": phone,
            "message": message[:160],
            "status": "DELIVERED",
        }
        self.sent_messages.append(record)
        return record
