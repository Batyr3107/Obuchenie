"""
Admin Service (Facade)

SRP: Этот модуль теперь служит фасадом для обратной совместимости.
ISP: Реальная логика разделена по сервисам:
- CourseModeratorService - модерация курсов
- UserManagementService - управление пользователями
- ReviewModeratorService - модерация отзывов

Импортируйте напрямую из подсервисов для новых проектов.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.user import User, UserRole

# Import from specialized services
from app.services.course_moderator_service import CourseModeratorService
from app.services.user_management_service import UserManagementService
from app.services.review_moderator_service import ReviewModeratorService


class AdminService:
    """
    Facade для административных операций.

    SOLID:
    - SRP: Делегирует специализированным сервисам
    - ISP: Клиенты могут использовать только нужные сервисы напрямую
    - DIP: Не зависит от конкретных реализаций

    Для новых проектов рекомендуется использовать сервисы напрямую:
    - CourseModeratorService
    - UserManagementService
    - ReviewModeratorService
    """

    # ============ МОДЕРАЦИЯ КУРСОВ ============
    # Делегирует CourseModeratorService

    @staticmethod
    async def get_pending_courses(
        db: Session,
        skip: int = 0,
        limit: int = 20
    ) -> List[Course]:
        """Получение курсов на модерации"""
        return await CourseModeratorService.get_pending_courses(db, skip, limit)

    @staticmethod
    async def approve_course(db: Session, course_id: int) -> Course:
        """Одобрение курса"""
        return await CourseModeratorService.approve_course(db, course_id)

    @staticmethod
    async def reject_course(db: Session, course_id: int) -> Course:
        """Отклонение курса"""
        return await CourseModeratorService.reject_course(db, course_id)

    # ============ УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ============
    # Делегирует UserManagementService

    @staticmethod
    async def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        role: Optional[UserRole] = None
    ) -> List[User]:
        """Получение списка пользователей с фильтрацией"""
        return await UserManagementService.get_users(db, skip, limit, search, role)

    @staticmethod
    async def block_user(db: Session, user_id: int) -> dict:
        """Блокировка пользователя"""
        return await UserManagementService.block_user(db, user_id)

    @staticmethod
    async def unblock_user(db: Session, user_id: int) -> dict:
        """Разблокировка пользователя"""
        return await UserManagementService.unblock_user(db, user_id)

    @staticmethod
    async def change_user_role(db: Session, user_id: int, new_role: UserRole) -> dict:
        """Изменение роли пользователя"""
        return await UserManagementService.change_user_role(db, user_id, new_role)

    # ============ МОДЕРАЦИЯ ОТЗЫВОВ ============
    # Делегирует ReviewModeratorService

    @staticmethod
    async def get_reported_reviews(
        db: Session,
        skip: int = 0,
        limit: int = 20
    ) -> List[dict]:
        """Получение отзывов с жалобами"""
        return await ReviewModeratorService.get_reported_reviews(db, skip, limit)

    @staticmethod
    async def block_review(db: Session, review_id: int) -> dict:
        """Блокировка отзыва"""
        return await ReviewModeratorService.block_review(db, review_id)

    @staticmethod
    async def resolve_report(db: Session, report_id: int) -> dict:
        """Отклонение жалобы"""
        return await ReviewModeratorService.resolve_report(db, report_id)
