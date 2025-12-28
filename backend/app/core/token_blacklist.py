"""
Token Blacklist Module

SRP: Отвечает только за черный список токенов (logout)
DIP: Использует абстракцию для хранилища
"""
from typing import Optional, Set, Protocol
from datetime import datetime, timezone
import hashlib
import logging

from jose import jwt, JWTError

from app.core.config import settings

logger = logging.getLogger(__name__)

BLACKLIST_PREFIX = "token_blacklist:"


class IBlacklistStorage(Protocol):
    """Protocol для хранилища blacklist (DIP)"""
    def setex(self, key: str, ttl: int, value: str) -> bool: ...
    def exists(self, key: str) -> int: ...


# In-memory fallback storage
_token_blacklist: Set[str] = set()
_blacklist_expiry: dict = {}

# Redis client (lazy init)
_redis_client: Optional[IBlacklistStorage] = None
_redis_checked = False


def _get_redis() -> Optional[IBlacklistStorage]:
    """Get Redis client with lazy initialization."""
    global _redis_client, _redis_checked

    if _redis_checked:
        return _redis_client

    _redis_checked = True

    try:
        import redis
        client = redis.Redis(
            host=getattr(settings, 'REDIS_HOST', 'localhost'),
            port=getattr(settings, 'REDIS_PORT', 6379),
            db=getattr(settings, 'REDIS_DB', 0),
            password=getattr(settings, 'REDIS_PASSWORD', None),
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        client.ping()
        _redis_client = client
        logger.info("Redis connected for token blacklist")
    except Exception as e:
        logger.warning(f"Redis not available for blacklist: {e}. Using in-memory fallback.")
        _redis_client = None

    return _redis_client


def _hash_token(token: str) -> str:
    """Create a hash of the token for storage (don't store raw tokens)."""
    return hashlib.sha256(token.encode()).hexdigest()[:32]


def _cleanup_expired_tokens() -> None:
    """Remove expired tokens from in-memory blacklist."""
    now = datetime.now(timezone.utc).timestamp()
    expired = [h for h, exp in _blacklist_expiry.items() if exp < now]
    for h in expired:
        _token_blacklist.discard(h)
        _blacklist_expiry.pop(h, None)


def blacklist_token(token: str) -> None:
    """
    Add a token to the blacklist (called on logout).

    SECURITY: Tokens are hashed before storage to prevent exposure.
    Uses Redis when available for horizontal scaling.

    Args:
        token: JWT token to blacklist
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = payload.get("exp")
        token_hash = _hash_token(token)

        redis = _get_redis()
        if redis:
            # Calculate TTL from token expiry
            ttl = int(exp - datetime.now(timezone.utc).timestamp()) if exp else 3600
            if ttl > 0:
                redis.setex(f"{BLACKLIST_PREFIX}{token_hash}", ttl, "1")
                logger.info("Token blacklisted in Redis")
        else:
            # Fallback to in-memory
            _token_blacklist.add(token_hash)
            if exp:
                _blacklist_expiry[token_hash] = exp
            _cleanup_expired_tokens()
            logger.info("Token blacklisted in memory (Redis unavailable)")

    except JWTError:
        pass  # Invalid token, no need to blacklist


def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token has been revoked.

    Args:
        token: JWT token to check

    Returns:
        True if token is blacklisted
    """
    token_hash = _hash_token(token)

    redis = _get_redis()
    if redis:
        try:
            return redis.exists(f"{BLACKLIST_PREFIX}{token_hash}") > 0
        except Exception:
            pass  # Fall through to in-memory check

    return token_hash in _token_blacklist
