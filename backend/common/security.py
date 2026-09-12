"""Security utilities for ThesisGuard."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from backend.common.config import settings


def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_hex(length)


def hash_value(value: str, salt: Optional[str] = None) -> str:
    """Hash a value with optional salt."""
    if salt is None:
        salt = generate_token(16)
    return hashlib.sha256(f"{salt}{value}".encode()).hexdigest()


def verify_hash(value: str, salt: str, expected_hash: str) -> bool:
    """Verify a hash value."""
    return hmac.compare_digest(hash_value(value, salt), expected_hash)


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(hours=24)

    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
