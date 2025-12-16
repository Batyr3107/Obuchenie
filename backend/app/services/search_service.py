"""
Search Service

ARCHITECTURE: Бизнес-логика для поиска и автозаполнения
PERFORMANCE: Оптимизированные запросы с фильтрацией
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.course import Course, CourseStatus
from app.core.validators import validate_search_query, sanitize_text


class SearchService:
    """Сервис для поиска и автозаполнения"""

    @staticmethod
    async def search_courses(
        db: Session,
        query: str,
        limit: int = 20
    ) -> List[Course]:
        """
        Поиск курсов по запросу

        SECURITY: Валидация и санитизация поискового запроса
        PERFORMANCE: ILIKE для регистронезависимого поиска

        Args:
            db: Database session
            query: Поисковый запрос
            limit: Максимальное количество результатов

        Returns:
            Список найденных курсов

        Raises:
            HTTPException: Если запрос некорректный
        """
        # SECURITY: Валидация запроса
        validated_query = validate_search_query(query)
        sanitized_query = sanitize_text(validated_query)

        # Поиск по названию и описанию
        search_pattern = f"%{sanitized_query}%"

        courses = db.query(Course).filter(
            Course.status == CourseStatus.APPROVED,
            or_(
                Course.title.ilike(search_pattern),
                Course.short_description.ilike(search_pattern)
            )
        ).order_by(
            # Сначала точные совпадения в названии
            func.lower(Course.title) == sanitized_query.lower(),
            # Потом по рейтингу
            Course.avg_rating.desc()
        ).limit(limit).all()

        return courses

    @staticmethod
    async def autocomplete(
        db: Session,
        query: str,
        limit: int = 10
    ) -> List[dict]:
        """
        Автозаполнение для поисковой строки

        Args:
            db: Database session
            query: Частичный поисковый запрос
            limit: Максимальное количество подсказок

        Returns:
            Список подсказок с id и title
        """
        if len(query) < 2:
            return []

        sanitized_query = sanitize_text(query)
        search_pattern = f"%{sanitized_query}%"

        courses = db.query(Course.id, Course.title).filter(
            Course.status == CourseStatus.APPROVED,
            Course.title.ilike(search_pattern)
        ).order_by(
            Course.avg_rating.desc()
        ).limit(limit).all()

        return [{"id": course.id, "title": course.title} for course in courses]

    @staticmethod
    async def get_popular_courses(
        db: Session,
        limit: int = 10
    ) -> List[Course]:
        """
        Получение популярных курсов

        LOGIC: Популярность = количество просмотров + отзывов + рейтинг

        Args:
            db: Database session
            limit: Максимальное количество курсов

        Returns:
            Список популярных курсов
        """
        popular_courses = db.query(Course).filter(
            Course.status == CourseStatus.APPROVED
        ).order_by(
            # Сначала по количеству отзывов (больше engagement)
            Course.total_reviews.desc(),
            # Потом по рейтингу
            Course.avg_rating.desc(),
            # Потом по просмотрам
            Course.views_count.desc()
        ).limit(limit).all()

        return popular_courses

    @staticmethod
    async def get_trending_courses(
        db: Session,
        limit: int = 10,
        days: int = 7
    ) -> List[Course]:
        """
        Получение трендовых курсов

        LOGIC: Курсы с недавней активностью (новые отзывы, просмотры)

        Args:
            db: Database session
            limit: Максимальное количество курсов
            days: Период для анализа (дней)

        Returns:
            Список трендовых курсов
        """
        from datetime import datetime, timedelta, timezone

        since_date = datetime.now(timezone.utc) - timedelta(days=days)

        # OPTIMIZATION: Можно добавить поле last_review_date в модель Course
        # для более эффективного запроса
        trending = db.query(Course).filter(
            Course.status == CourseStatus.APPROVED,
            Course.updated_at >= since_date
        ).order_by(
            Course.total_reviews.desc(),
            Course.avg_rating.desc()
        ).limit(limit).all()

        return trending
