"""
Rate limiting middleware для защиты API от спама и brute-force атак
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException


def get_remote_address_or_user(request: Request) -> str:
    """
    Получить идентификатор для rate limiting.
    Использует user_id из JWT если авторизован, иначе IP адрес.

    Best Practice: Per-user rate limiting for authenticated requests
    prevents one user from exhausting limits for others.
    """
    # Попробовать получить user_id из токена
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            from jose import jwt, JWTError
            from app.core.config import settings

            token = auth_header.split(" ")[1]
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except (JWTError, IndexError, ValueError):
            # Invalid token - fall back to IP-based limiting
            pass

    # Fallback на IP адрес
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Best Practice: Take first IP from X-Forwarded-For chain
        return f"ip:{forwarded.split(',')[0].strip()}"

    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"


# Создание limiter с динамическим storage
def get_storage_uri() -> str:
    """
    Получить storage URI для rate limiting

    PRODUCTION: Использует Redis для распределенного rate limiting
    DEVELOPMENT: Использует memory:// для простоты
    """
    from app.core.config import settings

    # В production используем Redis
    if settings.is_production() and settings.ENABLE_CACHE:
        return settings.get_redis_url()

    # В development используем память (по умолчанию)
    return settings.RATE_LIMIT_STORAGE


limiter = Limiter(
    key_func=get_remote_address_or_user,
    default_limits=["200/minute", "10000/day"],  # Глобальные лимиты
    storage_uri=get_storage_uri(),
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler для rate limit ошибок"""
    return HTTPException(
        status_code=429,
        detail={
            "error": "Rate limit exceeded",
            "message": "Слишком много запросов. Попробуйте позже.",
            "retry_after": exc.detail
        }
    )
