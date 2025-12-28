"""
User Management Service

SRP: Отвечает только за управление пользователями (админ-функции)
ISP: Минимальный интерфейс для управления пользователями
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.utils.db_helpers import get_or_404
from app.services.course_service import escape_like_pattern


class UserManagementService:
    """Сервис для управления пользователями"""

    @staticmethod
    async def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        role: Optional[UserRole] = None
    ) -> List[User]:
        """
        Получение списка пользователей с фильтрацией

        Args:
            db: Database session
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            search: Поисковый запрос (email или имя)
            role: Фильтр по роли

        Returns:
            Список пользователей
        """
        query = db.query(User)

        if search:
            # SECURITY: Escape LIKE wildcards to prevent injection
            safe_search = escape_like_pattern(search)
            query = query.filter(
                (User.email.ilike(f"%{safe_search}%", escape="\\")) |
                (User.full_name.ilike(f"%{safe_search}%", escape="\\"))
            )

        if role:
            query = query.filter(User.role == role)

        return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    async def block_user(db: Session, user_id: int) -> dict:
        """
        Блокировка пользователя

        Args:
            db: Database session
            user_id: ID пользователя

        Returns:
            Сообщение об успехе

        Raises:
            HTTPException: 404 если пользователь не найден
            HTTPException: 403 если попытка заблокировать админа
        """
        user = get_or_404(db, User, user_id, "User not found")

        if user.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot block admin"
            )

        user.is_blocked = True
        db.commit()

        return {"message": "User blocked successfully"}

    @staticmethod
    async def unblock_user(db: Session, user_id: int) -> dict:
        """
        Разблокировка пользователя

        Args:
            db: Database session
            user_id: ID пользователя

        Returns:
            Сообщение об успехе

        Raises:
            HTTPException: 404 если пользователь не найден
        """
        user = get_or_404(db, User, user_id, "User not found")
        user.is_blocked = False
        db.commit()

        return {"message": "User unblocked successfully"}

    @staticmethod
    async def change_user_role(db: Session, user_id: int, new_role: UserRole) -> dict:
        """
        Изменение роли пользователя

        Args:
            db: Database session
            user_id: ID пользователя
            new_role: Новая роль

        Returns:
            Сообщение об успехе

        Raises:
            HTTPException: 404 если пользователь не найден
        """
        user = get_or_404(db, User, user_id, "User not found")
        user.role = new_role
        db.commit()

        return {"message": f"User role changed to {new_role.value}"}
