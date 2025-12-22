from typing import Optional
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import is_token_blacklisted
from app.db.base import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

# Required authentication - throws 401 if no token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Optional authentication - returns None if no token (doesn't throw 401)
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False  # Don't throw 401, return None instead
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Получение текущего авторизованного пользователя.

    SECURITY: Checks token blacklist for revoked tokens (logout).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Check if token has been revoked (logout)
    if is_token_blacklisted(token):
        logger.warning("Attempt to use blacklisted (revoked) token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        logger.warning(f"Inactive user {user.id} ({user.email}) attempted access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    if user.is_blocked:
        logger.warning(f"Blocked user {user.id} ({user.email}) attempted access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is blocked")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверка, что пользователь активен и верифицирован"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверка, что пользователь - администратор"""
    from app.models.user import UserRole
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# Опциональная аутентификация (для неавторизованных пользователей)
async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Получение пользователя если есть валидный токен, иначе None.

    SECURITY: Uses oauth2_scheme_optional with auto_error=False,
    so missing/invalid tokens return None instead of 401.
    Also checks token blacklist for revoked tokens.

    Use case: Endpoints that work differently for auth vs anon users
    (e.g., showing "Add to favorites" button only for logged-in users).
    """
    if not token:
        return None

    # Check if token has been revoked
    if is_token_blacklisted(token):
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active or user.is_blocked:
        return None

    return user
