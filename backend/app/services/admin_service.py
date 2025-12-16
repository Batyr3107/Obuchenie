"""
Admin Service

ARCHITECTURE: Бизнес-логика для административных операций
DRY: Централизация логики модерации и управления
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime, timezone

from app.models.course import Course, CourseStatus
from app.models.user import User, UserRole
from app.models.review import Review
from app.models.report import Report, ReportStatus
from app.utils.db_helpers import get_or_404


class AdminService:
    """Сервис для административных операций"""

    # ============ МОДЕРАЦИЯ КУРСОВ ============

    @staticmethod
    async def get_pending_courses(
        db: Session,
        skip: int = 0,
        limit: int = 20
    ) -> List[Course]:
        """
        Получение курсов на модерации

        Args:
            db: Database session
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            Список курсов на модерации
        """
        courses = db.query(Course).filter(
            Course.status == CourseStatus.PENDING
        ).order_by(Course.created_at.desc()).offset(skip).limit(limit).all()

        return courses

    @staticmethod
    async def approve_course(db: Session, course_id: int) -> Course:
        """
        Одобрение курса

        Args:
            db: Database session
            course_id: ID курса

        Returns:
            Одобренный курс

        Raises:
            HTTPException: 404 если курс не найден
        """
        course = get_or_404(db, Course, course_id, "Course not found")
        course.status = CourseStatus.APPROVED
        db.commit()
        db.refresh(course)

        return course

    @staticmethod
    async def reject_course(db: Session, course_id: int) -> Course:
        """
        Отклонение курса

        Args:
            db: Database session
            course_id: ID курса

        Returns:
            Отклоненный курс

        Raises:
            HTTPException: 404 если курс не найден
        """
        course = get_or_404(db, Course, course_id, "Course not found")
        course.status = CourseStatus.REJECTED
        db.commit()
        db.refresh(course)

        return course

    # ============ УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ============

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
            query = query.filter(
                (User.email.ilike(f"%{search}%")) |
                (User.full_name.ilike(f"%{search}%"))
            )

        if role:
            query = query.filter(User.role == role)

        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        return users

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
        from fastapi import HTTPException, status

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

        return {"message": f"User role changed to {new_role}"}

    # ============ МОДЕРАЦИЯ ОТЗЫВОВ ============

    @staticmethod
    async def get_reported_reviews(
        db: Session,
        skip: int = 0,
        limit: int = 20
    ) -> List[dict]:
        """
        Получение отзывов с жалобами

        PERFORMANCE: Использует joinedload для предотвращения N+1 queries

        Args:
            db: Database session
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            Список отзывов с жалобами
        """
        reports = db.query(Report).options(
            joinedload(Report.review).joinedload(Review.user),
            joinedload(Report.review).joinedload(Review.course),
            joinedload(Report.user)
        ).filter(
            Report.status == ReportStatus.PENDING
        ).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

        # Группировка по отзывам
        review_reports = {}
        for report in reports:
            if report.review_id not in review_reports:
                review_reports[report.review_id] = {
                    "review": report.review,
                    "reports": []
                }
            review_reports[report.review_id]["reports"].append(report)

        return list(review_reports.values())

    @staticmethod
    async def block_review(db: Session, review_id: int) -> dict:
        """
        Блокировка отзыва

        TRANSACTIONAL: Атомарная операция с обновлением всех связанных жалоб

        Args:
            db: Database session
            review_id: ID отзыва

        Returns:
            Сообщение об успехе

        Raises:
            HTTPException: 404 если отзыв не найден
        """
        review = get_or_404(db, Review, review_id, "Review not found")

        review.is_blocked = True
        review.is_approved = False

        # Обновить статус всех жалоб на этот отзыв
        db.query(Report).filter(Report.review_id == review_id).update({
            "status": ReportStatus.RESOLVED,
            "resolved_at": datetime.now(timezone.utc)
        })

        db.commit()

        return {"message": "Review blocked successfully"}

    @staticmethod
    async def resolve_report(db: Session, report_id: int) -> dict:
        """
        Отклонение жалобы (отзыв нормальный)

        Args:
            db: Database session
            report_id: ID жалобы

        Returns:
            Сообщение об успехе

        Raises:
            HTTPException: 404 если жалоба не найдена
        """
        report = get_or_404(db, Report, report_id, "Report not found")
        report.status = ReportStatus.REJECTED
        report.resolved_at = datetime.now(timezone.utc)
        db.commit()

        return {"message": "Report rejected"}
