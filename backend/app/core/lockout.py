"""
Account Lockout Module

SRP: Отвечает только за блокировку аккаунтов при brute-force атаках
DIP: Использует абстракцию IRedisClient
"""
from typing import Optional, Protocol
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

LOGIN_ATTEMPTS_PREFIX = "login_attempts:"


class IRedisClient(Protocol):
    """Protocol для Redis клиента (DIP)"""
    def incr(self, key: str) -> int: ...
    def expire(self, key: str, seconds: int) -> bool: ...
    def get(self, key: str) -> Optional[str]: ...
    def delete(self, key: str) -> int: ...


# Lazy-initialized Redis client
_redis_client: Optional[IRedisClient] = None
_redis_checked = False


def _get_redis() -> Optional[IRedisClient]:
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
        logger.info("Redis connected for account lockout")
    except Exception as e:
        logger.warning(f"Redis not available for lockout: {e}. Lockout disabled.")
        _redis_client = None

    return _redis_client


def record_failed_login(email: str) -> int:
    """
    Record a failed login attempt for an email.

    SECURITY: Prevents brute-force attacks by tracking failed attempts.

    Args:
        email: User's email address

    Returns:
        Current number of failed attempts
    """
    key = f"{LOGIN_ATTEMPTS_PREFIX}{email.lower()}"
    timeout = getattr(settings, 'LOGIN_ATTEMPT_TIMEOUT', 900)  # 15 min default

    redis = _get_redis()
    if redis:
        try:
            attempts = redis.incr(key)
            if attempts == 1:
                redis.expire(key, timeout)
            return attempts
        except Exception:
            pass

    # Fallback - no tracking without Redis
    return 0


def get_failed_login_attempts(email: str) -> int:
    """Get current failed login attempts for an email."""
    key = f"{LOGIN_ATTEMPTS_PREFIX}{email.lower()}"

    redis = _get_redis()
    if redis:
        try:
            attempts = redis.get(key)
            return int(attempts) if attempts else 0
        except Exception:
            pass

    return 0


def clear_failed_login_attempts(email: str) -> None:
    """Clear failed login attempts after successful login."""
    key = f"{LOGIN_ATTEMPTS_PREFIX}{email.lower()}"

    redis = _get_redis()
    if redis:
        try:
            redis.delete(key)
        except Exception:
            pass


def is_account_locked(email: str) -> bool:
    """
    Check if account is locked due to too many failed attempts.

    Args:
        email: User's email address

    Returns:
        True if account is locked
    """
    max_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
    return get_failed_login_attempts(email) >= max_attempts
