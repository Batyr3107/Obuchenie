"""
JWT Token Module

SRP: Отвечает только за создание и валидацию JWT токенов
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from jose import jwt

from app.core.config import settings


def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создание JWT токена.

    Args:
        subject: ID пользователя или другой идентификатор
        expires_delta: Время жизни токена

    Returns:
        Закодированный JWT токен
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Декодирование JWT токена.

    Args:
        token: JWT токен

    Returns:
        Payload токена

    Raises:
        JWTError: Если токен невалидный
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
