"""
User Service

ARCHITECTURE: Бизнес-логика для работы с пользователями
TESTABILITY: Легко тестируется без HTTP слоя
SECURITY: Handles race conditions in user registration
"""
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import (
    get_password_hash,
    verify_password,
    is_account_locked,
    record_failed_login,
    clear_failed_login_attempts
)
from app.core.validators import validate_email, sanitize_text
from app.core.config import settings


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    async def register_user(db: Session, user_data: UserCreate) -> User:
        """
        Регистрация нового пользователя

        CLEAN CODE: Вся логика регистрации в одном месте
        TESTABILITY: Можно тестировать без HTTP
        SECURITY: Uses try/except IntegrityError to prevent TOCTOU race condition.
                  The database UNIQUE constraint is the source of truth.

        Args:
            db: Database session
            user_data: Данные пользователя

        Returns:
            Созданный пользователь

        Raises:
            HTTPException: 400 если email уже зарегистрирован
        """
        # Валидация и санитизация
        validated_email = validate_email(user_data.email)
        sanitized_full_name = sanitize_text(user_data.full_name, max_length=200)

        # Создание пользователя
        new_user = User(
            email=validated_email,
            hashed_password=get_password_hash(user_data.password),
            full_name=sanitized_full_name
        )

        # SECURITY: Rely on DB unique constraint, not check-then-insert (TOCTOU)
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except IntegrityError as e:
            db.rollback()
            # Check if it's a duplicate email error
            if "email" in str(e.orig).lower() or "unique" in str(e.orig).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            # Re-raise for other integrity errors
            raise

        return new_user

    @staticmethod
    async def authenticate_user(
        db: Session,
        email: str,
        password: str
    ) -> User:
        """
        Аутентификация пользователя с защитой от brute-force.

        SECURITY:
        - Account lockout after MAX_LOGIN_ATTEMPTS failed attempts
        - Tracks failed attempts in Redis (or skips if unavailable)
        - Clears attempts on successful login

        Args:
            db: Database session
            email: Email пользователя
            password: Пароль

        Returns:
            Аутентифицированный пользователь

        Raises:
            HTTPException: 429 если аккаунт заблокирован
            HTTPException: 401 если credentials неверные
            HTTPException: 400 если пользователь неактивен
        """
        # Валидация email
        validated_email = validate_email(email)

        # SECURITY: Check if account is locked
        if is_account_locked(validated_email):
            timeout = getattr(settings, 'LOGIN_ATTEMPT_TIMEOUT', 900)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account temporarily locked. Try again in {timeout // 60} minutes.",
                headers={"Retry-After": str(timeout)},
            )

        # Поиск пользователя
        user = db.query(User).filter(User.email == validated_email).first()

        # Проверка пароля
        if not user or not verify_password(password, user.hashed_password):
            # Record failed attempt
            attempts = record_failed_login(validated_email)
            max_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
            remaining = max(0, max_attempts - attempts)

            detail = "Incorrect email or password"
            if remaining > 0 and remaining <= 3:
                detail = f"{detail}. {remaining} attempts remaining."

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=detail,
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Проверка активности
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        # SECURITY: Clear failed attempts on successful login
        clear_failed_login_attempts(validated_email)

        return user

    @staticmethod
    def update_last_login(db: Session, user: User) -> None:
        """
        Обновление времени последнего входа

        Args:
            db: Database session
            user: Пользователь для обновления
        """
        user.last_login = datetime.now(timezone.utc)
        db.commit()

    @staticmethod
    async def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Получить пользователя по ID

        Args:
            db: Database session
            user_id: ID пользователя

        Returns:
            Пользователь или None
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    async def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Получить пользователя по email

        Args:
            db: Database session
            email: Email пользователя

        Returns:
            Пользователь или None
        """
        validated_email = validate_email(email)
        return db.query(User).filter(User.email == validated_email).first()

    @staticmethod
    async def update_user_profile(
        db: Session,
        user: User,
        full_name: Optional[str] = None
    ) -> User:
        """
        Обновление профиля пользователя

        Args:
            db: Database session
            user: Пользователь для обновления
            full_name: Новое имя (опционально)

        Returns:
            Обновленный пользователь
        """
        if full_name:
            user.full_name = sanitize_text(full_name, max_length=200)

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    async def deactivate_user(db: Session, user: User) -> User:
        """
        Деактивация пользователя

        Args:
            db: Database session
            user: Пользователь для деактивации

        Returns:
            Деактивированный пользователь
        """
        user.is_active = False
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    async def activate_user(db: Session, user: User) -> User:
        """
        Активация пользователя

        Args:
            db: Database session
            user: Пользователь для активации

        Returns:
            Активированный пользователь
        """
        user.is_active = True
        db.commit()
        db.refresh(user)

        return user
