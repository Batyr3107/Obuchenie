"""
Rate limiting middleware для защиты API от спама и brute-force атак
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException


def get_remote_address_or_user(request: Request) -> str:
    """
    Получить идентификатор для rate limiting
    Использует IP адрес или user_id если авторизован
    """
    # Попробовать получить user_id из токена
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            # Можно извлечь user_id из JWT токена
            # Для простоты используем IP
            pass
        except:
            pass

    # Fallback на IP адрес
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]

    return request.client.host if request.client else "unknown"


# Создание limiter
limiter = Limiter(
    key_func=get_remote_address_or_user,
    default_limits=["200/minute", "10000/day"],  # Глобальные лимиты
    storage_uri="memory://",  # В production использовать Redis
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
