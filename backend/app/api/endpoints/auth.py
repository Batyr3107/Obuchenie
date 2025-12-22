from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.security import create_access_token, blacklist_token
from app.core.config import settings
from app.api.dependencies.auth import get_current_user
from app.core.rate_limit import limiter
from app.services.user_service import UserService

# For logout endpoint to get raw token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
async def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя

    CLEAN CODE: Вся бизнес-логика в UserService
    Endpoint всего ~3 строки вместо 30!
    """
    user = await UserService.register_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Вход пользователя

    CLEAN CODE: Вся бизнес-логика в UserService
    Endpoint всего ~8 строк вместо 30!
    """
    # Аутентификация
    user = await UserService.authenticate_user(db, form_data.username, form_data.password)

    # Обновление времени последнего входа
    UserService.update_last_login(db, user)

    # Создание токена
    access_token = create_access_token(subject=user.id)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    return current_user


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user)
):
    """
    Выход пользователя.

    SECURITY: Добавляет токен в blacklist, делая его недействительным
    даже до истечения срока действия.

    Returns:
        Сообщение об успешном выходе
    """
    blacklist_token(token)
    return {"message": "Successfully logged out"}
