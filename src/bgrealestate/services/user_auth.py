"""User authentication service — registration, login, JWT tokens.

Uses HMAC-SHA256 JWTs for session-less auth. Password hashing uses
hashlib.pbkdf2_hmac (stdlib) to avoid external dependencies for the MVP.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from typing import Any

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_EXPIRY_SECONDS = int(os.getenv("JWT_EXPIRY_SECONDS", "86400"))
VALID_USER_MODES = frozenset({"buyer", "renter", "seller", "agent"})


@dataclass(frozen=True)
class TokenPayload:
    user_id: str
    email: str
    user_mode: str
    exp: int


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"pbkdf2:sha256:100000${salt}${dk.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        _, _, rest = password_hash.partition("pbkdf2:sha256:100000$")
        if not rest:
            return False
        salt, _, stored_hash = rest.partition("$")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
        return hmac.compare_digest(dk.hex(), stored_hash)
    except Exception:
        return False


def create_jwt(user_id: str, email: str, user_mode: str) -> str:
    header = urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).rstrip(b"=")
    payload_dict: dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "mode": user_mode,
        "exp": int(time.time()) + JWT_EXPIRY_SECONDS,
    }
    payload = urlsafe_b64encode(json.dumps(payload_dict).encode()).rstrip(b"=")
    signing_input = header + b"." + payload
    signature = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    sig_b64 = urlsafe_b64encode(signature).rstrip(b"=")
    return (signing_input + b"." + sig_b64).decode()


def decode_jwt(token: str) -> TokenPayload | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        signing_input = (parts[0] + "." + parts[1]).encode()
        sig = urlsafe_b64decode(parts[2] + "==")
        expected = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload_json = urlsafe_b64decode(parts[1] + "==")
        data = json.loads(payload_json)
        if data.get("exp", 0) < time.time():
            return None
        return TokenPayload(
            user_id=data["sub"],
            email=data["email"],
            user_mode=data.get("mode", "buyer"),
            exp=data["exp"],
        )
    except Exception:
        return None
