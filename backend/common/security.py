"""Security utilities for ThesisGuard.

提供密码学安全的 token 生成、SHA-256 哈希（带盐）和 JWT 编解码。
当前 V1 阶段仅作基础设施预留，前端暂不强制鉴权。
注意：verify_hash 使用 hmac.compare_digest 防止时序攻击。
"""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from backend.common.config import settings


def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_hex(length)


def hash_value(value: str, salt: str | None = None) -> str:
    """Hash a value with optional salt."""
    if salt is None:
        salt = generate_token(16)
    return hashlib.sha256(f"{salt}{value}".encode()).hexdigest()


def verify_hash(value: str, salt: str, expected_hash: str) -> bool:
    """Verify a hash value."""
    # compare_digest 恒定时间比较，防止时序侧信道攻击
    return hmac.compare_digest(hash_value(value, salt), expected_hash)


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(hours=24)

    expire = datetime.now(UTC) + expires_delta
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> dict | None:
    """Decode and verify a JWT access token."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
