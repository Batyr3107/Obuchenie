from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Set
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
import hashlib
import logging

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============= Redis Client (Lazy Initialization) =============
_redis_client = None


def _get_redis():
    """Get Redis client with lazy initialization."""
    global _redis_client
    if _redis_client is None:
        try:
            import redis
            _redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=getattr(settings, 'REDIS_DB', 0),
                password=getattr(settings, 'REDIS_PASSWORD', None),
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            _redis_client.ping()
            logger.info("Redis connected for token blacklist")
        except Exception as e:
            logger.warning(f"Redis not available for blacklist: {e}. Using in-memory fallback.")
            _redis_client = False  # Mark as unavailable
    return _redis_client if _redis_client else None


# ============= Token Blacklist =============
# Uses Redis when available, falls back to in-memory storage.
# In-memory fallback is NOT suitable for production with multiple workers!

_token_blacklist: Set[str] = set()  # Fallback for when Redis is unavailable
_blacklist_expiry: dict = {}

BLACKLIST_PREFIX = "token_blacklist:"


def _hash_token(token: str) -> str:
    """Create a hash of the token for storage (don't store raw tokens)."""
    return hashlib.sha256(token.encode()).hexdigest()[:32]


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


def _cleanup_expired_tokens() -> None:
    """Remove expired tokens from in-memory blacklist."""
    now = datetime.now(timezone.utc).timestamp()
    expired = [h for h, exp in _blacklist_expiry.items() if exp < now]
    for h in expired:
        _token_blacklist.discard(h)
        _blacklist_expiry.pop(h, None)


# ============= Account Lockout =============
# Protects against brute-force password attacks

LOGIN_ATTEMPTS_PREFIX = "login_attempts:"


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
