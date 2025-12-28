"""
Course Moderator Service

SRP: Отвечает только за модерацию курсов
ISP: Минимальный интерфейс для модерации курсов
"""
from typing import List
from sqlalchemy.orm import Session

from app.models.course import Course, CourseStatus
from app.utils.db_helpers import get_or_404


class CourseModeratorService:
    """Сервис для модерации курсов"""

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
        return db.query(Course).filter(
            Course.status == CourseStatus.PENDING
        ).order_by(Course.created_at.desc()).offset(skip).limit(limit).all()

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
