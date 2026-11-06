"""Sample Application: Authentication & Authorization Service."""

import hashlib
import time
from typing import Dict, Optional


class AuthService:
    def __init__(self):
        self._users: Dict[str, Dict] = {}
        self._tokens: Dict[str, str] = {}

    def register(self, username: str, password: str, role: str = "developer") -> Dict:
        if not username or not password:
            raise ValueError("Username and password must not be empty.")
        if username in self._users:
            raise ValueError(f"User {username} already exists.")
        
        salt = "ci_cd_secure_salt"
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        self._users[username] = {"password_hash": hashed, "role": role, "active": True}
        return {"username": username, "role": role, "status": "created"}

    def authenticate(self, username: str, password: str) -> Optional[str]:
        user = self._users.get(username)
        if not user or not user["active"]:
            return None
        salt = "ci_cd_secure_salt"
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        if user["password_hash"] == hashed:
            token = f"tok_{username}_{int(time.time())}"
            self._tokens[token] = username
            return token
        return None

    def verify_token(self, token: str) -> Optional[str]:
        return self._tokens.get(token)

    def deactivate_user(self, username: str) -> bool:
        if username in self._users:
            self._users[username]["active"] = False
            return True
        return False
