from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.base import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.dependencies.auth import get_current_user
from app.core.rate_limit import limiter
from app.core.validators import validate_email, sanitize_text

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
async def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""

    # Валидация и санитизация входных данных
    validated_email = validate_email(user_data.email)
    sanitized_full_name = sanitize_text(user_data.full_name, max_length=200)

    # Проверка, существует ли пользователь
    existing_user = db.query(User).filter(User.email == validated_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Создание нового пользователя
    new_user = User(
        email=validated_email,
        hashed_password=get_password_hash(user_data.password),
        full_name=sanitized_full_name
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Вход пользователя"""

    # Валидация email
    validated_email = validate_email(form_data.username)

    # Поиск пользователя
    user = db.query(User).filter(User.email == validated_email).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Обновление времени последнего входа
    user.last_login = datetime.utcnow()
    db.commit()

    # Создание токена
    access_token = create_access_token(subject=user.id)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    return current_user
