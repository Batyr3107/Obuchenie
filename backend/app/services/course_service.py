"""
Course Service

ARCHITECTURE: Бизнес-логика для работы с курсами
TESTABILITY: Легко тестируется без HTTP слоя
PERFORMANCE: Кэширование списков курсов
SECURITY: Safe LIKE patterns with proper escaping
CONCURRENCY: Handles slug collisions with retry logic
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from slugify import slugify
import uuid

from app.models.course import Course, CourseStatus
from app.schemas.course import CourseCreate, CourseUpdate
from app.utils.db_helpers import get_or_404, atomic_increment
from app.core.cache import cache_manager


def escape_like_pattern(search: str) -> str:
    """
    Escape special LIKE pattern characters to prevent wildcard injection.

    SECURITY: Prevents attacks where users manipulate search with % or _ chars.
    Example: searching "%" would match everything without this escape.

    Args:
        search: Raw search string from user input

    Returns:
        Escaped string safe for use in LIKE/ILIKE queries
    """
    return (
        search
        .replace("\\", "\\\\")  # Escape backslash first
        .replace("%", "\\%")    # Escape percent
        .replace("_", "\\_")    # Escape underscore
    )


class CourseService:
    """Сервис для работы с курсами"""

    CACHE_KEY_PREFIX = "courses_list"
    CACHE_TTL = 1800  # 30 минут (курсы обновляются чаще чем категории)

    @staticmethod
    async def get_courses(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        min_rating: Optional[float] = None,
        status: CourseStatus = CourseStatus.APPROVED
    ) -> List[Course]:
        """
        Получение списка курсов с фильтрацией

        PERFORMANCE:
        - Использует joinedload для предотвращения N+1 queries
        - Кэширование результатов на 30 минут

        Args:
            db: Database session
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            category_id: ID категории для фильтрации
            search: Поисковый запрос
            min_rating: Минимальный рейтинг
            status: Статус курса (по умолчанию APPROVED)

        Returns:
            Список курсов
        """
        # Генерация ключа кэша на основе параметров
        cache_key = f"{CourseService.CACHE_KEY_PREFIX}:{status}:{skip}:{limit}:{category_id}:{search}:{min_rating}"

        # Проверка кэша (только для APPROVED курсов)
        if status == CourseStatus.APPROVED:
            cached = cache_manager.get(cache_key)
            if cached is not None:
                return cached

        # PERFORMANCE: joinedload для предотвращения N+1 queries
        query = db.query(Course).options(
            joinedload(Course.category),
            joinedload(Course.subcategory)
        ).filter(Course.status == status)

        # Фильтрация по категории
        if category_id:
            query = query.filter(Course.category_id == category_id)

        # Поиск по названию (SECURITY: escape LIKE wildcards)
        if search:
            safe_search = escape_like_pattern(search)
            query = query.filter(Course.title.ilike(f"%{safe_search}%", escape="\\"))

        # Фильтрация по рейтингу
        if min_rating:
            query = query.filter(Course.avg_rating >= min_rating)

        # Сортировка по рейтингу (по умолчанию)
        query = query.order_by(Course.avg_rating.desc())

        courses = query.offset(skip).limit(limit).all()

        # Сохранение в кэш (только для APPROVED курсов)
        if status == CourseStatus.APPROVED:
            cache_manager.set(cache_key, courses, expire=CourseService.CACHE_TTL)

        return courses

    @staticmethod
    async def get_course_by_id(db: Session, course_id: int) -> Course:
        """
        Получение курса по ID

        PERFORMANCE: Loads category, subcategory, and tags.
        Reviews are NOT loaded here - use /reviews?course_id=X for paginated reviews.

        Args:
            db: Database session
            course_id: ID курса

        Returns:
            Курс

        Raises:
            HTTPException: 404 если курс не найден
        """
        # NOTE: Reviews removed from joinedload to prevent loading 10000+ reviews
        # Use GET /reviews?course_id=X with pagination instead
        course = db.query(Course).options(
            joinedload(Course.category),
            joinedload(Course.subcategory),
            joinedload(Course.tags)
        ).filter(Course.id == course_id).first()

        if not course:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        return course

    @staticmethod
    def increment_views(db: Session, course: Course) -> None:
        """
        Увеличение счетчика просмотров

        CONCURRENCY: Uses atomic SQL increment to prevent race conditions.
        Without this, concurrent requests could cause lost updates.

        Args:
            db: Database session
            course: Курс для обновления
        """
        atomic_increment(db, Course, course.id, "views_count")
        db.commit()

    @staticmethod
    async def create_course(db: Session, course_data: CourseCreate) -> Course:
        """
        Создание нового курса

        BUSINESS LOGIC: Генерирует slug, проверяет уникальность
        CONCURRENCY: Uses retry with unique suffix to handle slug collisions

        Args:
            db: Database session
            course_data: Данные курса

        Returns:
            Созданный курс (со статусом PENDING)
        """
        base_slug = slugify(course_data.title)
        max_retries = 3

        for attempt in range(max_retries):
            # Generate slug with suffix on retry
            if attempt == 0:
                slug = base_slug
            elif attempt == 1:
                slug = f"{base_slug}-{course_data.category_id}"
            else:
                # Use short UUID suffix for guaranteed uniqueness
                slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

            # Создание курса
            new_course = Course(
                title=course_data.title,
                slug=slug,
                short_description=course_data.short_description,
                full_description=course_data.full_description,
                official_url=course_data.official_url,
                logo_url=course_data.logo_url,
                category_id=course_data.category_id,
                subcategory_id=course_data.subcategory_id,
                format=course_data.format,
                price_type=course_data.price_type,
                price_amount=course_data.price_amount,
                currency=course_data.currency,
                duration_hours=course_data.duration_hours,
                duration_weeks=course_data.duration_weeks,
                language=course_data.language,
                has_certificate=course_data.has_certificate,
                difficulty_level=course_data.difficulty_level,
                requirements=course_data.requirements,
                what_you_learn=course_data.what_you_learn,
                country=course_data.country,
                city=course_data.city,
                status=CourseStatus.PENDING  # Требует модерации
            )

            try:
                db.add(new_course)
                db.commit()
                db.refresh(new_course)
                break  # Success
            except IntegrityError as e:
                db.rollback()
                # If it's a slug collision, retry with different slug
                if "slug" in str(e.orig).lower() and attempt < max_retries - 1:
                    continue
                # Re-raise for other errors or last attempt
                raise

        # Инвалидация кэша (новый курс добавлен)
        CourseService._invalidate_cache()

        return new_course

    @staticmethod
    async def update_course(
        db: Session,
        course_id: int,
        course_data: CourseUpdate
    ) -> Course:
        """
        Обновление курса

        Args:
            db: Database session
            course_id: ID курса
            course_data: Данные для обновления

        Returns:
            Обновленный курс

        Raises:
            HTTPException: 404 если курс не найден
        """
        course = get_or_404(db, Course, course_id)

        # Обновление полей
        update_data = course_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)

        db.commit()
        db.refresh(course)

        # Инвалидация кэша (курс обновлен)
        CourseService._invalidate_cache()

        return course

    @staticmethod
    async def delete_course(db: Session, course_id: int) -> None:
        """
        Удаление курса

        Args:
            db: Database session
            course_id: ID курса

        Raises:
            HTTPException: 404 если курс не найден
        """
        course = get_or_404(db, Course, course_id)
        db.delete(course)
        db.commit()

        # Инвалидация кэша (курс удален)
        CourseService._invalidate_cache()

    @staticmethod
    async def approve_course(db: Session, course_id: int) -> Course:
        """
        Одобрение курса (модерация)

        Args:
            db: Database session
            course_id: ID курса

        Returns:
            Одобренный курс

        Raises:
            HTTPException: 404 если курс не найден
        """
        course = get_or_404(db, Course, course_id)
        course.status = CourseStatus.APPROVED
        db.commit()
        db.refresh(course)

        # Инвалидация кэша (курс одобрен и теперь доступен)
        CourseService._invalidate_cache()

        return course

    @staticmethod
    async def reject_course(db: Session, course_id: int) -> Course:
        """
        Отклонение курса (модерация)

        Args:
            db: Database session
            course_id: ID курса

        Returns:
            Отклоненный курс

        Raises:
            HTTPException: 404 если курс не найден
        """
        course = get_or_404(db, Course, course_id)
        course.status = CourseStatus.REJECTED
        db.commit()
        db.refresh(course)

        # Инвалидация кэша (курс отклонен)
        CourseService._invalidate_cache()

        return course

    @staticmethod
    async def get_pending_courses(db: Session, skip: int = 0, limit: int = 20) -> List[Course]:
        """
        Получение курсов на модерации

        Args:
            db: Database session
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            Список курсов на модерации
        """
        return await CourseService.get_courses(
            db,
            skip=skip,
            limit=limit,
            status=CourseStatus.PENDING
        )

    @staticmethod
    def _invalidate_cache() -> None:
        """
        Инвалидация кэша списков курсов

        Вызывается после create/update/delete/approve/reject операций
        """
        cache_manager.clear_pattern(f"{CourseService.CACHE_KEY_PREFIX}:*")
