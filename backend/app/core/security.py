from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Set
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
import hashlib
import logging

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============= Token Blacklist =============
# WARNING: In-memory blacklist is NOT suitable for production with multiple workers!
# Use Redis in production: settings.get_redis_url()
#
# This is a simple implementation that:
# 1. Stores hashes of revoked tokens (not full tokens for security)
# 2. Automatically expires entries based on token expiry
# 3. Should be replaced with Redis for horizontal scaling

_token_blacklist: Set[str] = set()
_blacklist_expiry: dict = {}  # token_hash -> expiry_timestamp


def _hash_token(token: str) -> str:
    """Create a hash of the token for storage (don't store raw tokens)."""
    return hashlib.sha256(token.encode()).hexdigest()[:32]


def blacklist_token(token: str) -> None:
    """
    Add a token to the blacklist (called on logout).

    SECURITY: Tokens are hashed before storage to prevent exposure.

    Args:
        token: JWT token to blacklist
    """
    try:
        # Get token expiry from payload
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = payload.get("exp")

        token_hash = _hash_token(token)
        _token_blacklist.add(token_hash)

        if exp:
            _blacklist_expiry[token_hash] = exp

        # Cleanup expired entries (basic garbage collection)
        _cleanup_expired_tokens()

        logger.info(f"Token blacklisted successfully")
    except JWTError:
        # Token is invalid anyway, no need to blacklist
        pass


def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token has been revoked.

    Args:
        token: JWT token to check

    Returns:
        True if token is blacklisted
    """
    token_hash = _hash_token(token)
    return token_hash in _token_blacklist


def _cleanup_expired_tokens() -> None:
    """Remove expired tokens from blacklist to prevent memory growth."""
    now = datetime.now(timezone.utc).timestamp()
    expired_hashes = [
        h for h, exp in _blacklist_expiry.items()
        if exp < now
    ]
    for h in expired_hashes:
        _token_blacklist.discard(h)
        _blacklist_expiry.pop(h, None)


def create_access_token(subject: Union[str, int], expires_delta: Optional[timedelta] = None) -> str:
    """
    Создание JWT токена.

    Best Practice: Use datetime.now(timezone.utc) instead of deprecated datetime.utcnow()
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)
