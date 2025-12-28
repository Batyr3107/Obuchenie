"""
Favorite Service

ARCHITECTURE: Бизнес-логика для работы с избранным
"""
from typing import List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status

from app.models.favorite import Favorite
from app.models.course import Course
from app.utils.db_helpers import get_or_404, atomic_increment


class FavoriteService:
    """Сервис для работы с избранным"""

    @staticmethod
    async def add_to_favorites(db: Session, user_id: int, course_id: int) -> Favorite:
        """
        Добавление курса в избранное

        Args:
            db: Database session
            user_id: ID пользователя
            course_id: ID курса

        Returns:
            Созданная запись избранного

        Raises:
            HTTPException: 404 если курс не найден
            HTTPException: 400 если уже в избранном
        """
        # Проверка существования курса
        course = get_or_404(db, Course, course_id)

        # SECURITY: No TOCTOU - rely on IntegrityError from UNIQUE constraint
        try:
            favorite = Favorite(user_id=user_id, course_id=course_id)
            db.add(favorite)
            db.flush()  # Get ID before atomic increment

            # CONCURRENCY: Atomic increment prevents race conditions
            atomic_increment(db, Course, course_id, "favorites_count")

            db.commit()
            db.refresh(favorite)

            return favorite
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Course already in favorites"
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add favorite"
            )

    @staticmethod
    async def remove_from_favorites(db: Session, user_id: int, course_id: int) -> None:
        """
        Удаление курса из избранного

        Args:
            db: Database session
            user_id: ID пользователя
            course_id: ID курса

        Raises:
            HTTPException: 404 если не найдено в избранном
        """
        favorite = db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.course_id == course_id
        ).first()

        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorite not found"
            )

        try:
            db.delete(favorite)

            # CONCURRENCY: Atomic decrement prevents race conditions
            atomic_increment(db, Course, course_id, "favorites_count", -1)

            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove favorite"
            )

    @staticmethod
    async def get_user_favorites(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Favorite]:
        """
        Получение избранных курсов пользователя

        PERFORMANCE: Использует joinedload для предотвращения N+1 queries

        Args:
            db: Database session
            user_id: ID пользователя
            skip: Пропуск записей
            limit: Лимит записей

        Returns:
            Список избранных
        """
        favorites = db.query(Favorite).options(
            joinedload(Favorite.course)
        ).filter(
            Favorite.user_id == user_id
        ).order_by(
            Favorite.created_at.desc()
        ).offset(skip).limit(limit).all()

        return favorites

    @staticmethod
    async def is_favorite(db: Session, user_id: int, course_id: int) -> bool:
        """
        Проверка, находится ли курс в избранном

        PERFORMANCE: Uses exists() instead of first() to avoid fetching full row

        Args:
            db: Database session
            user_id: ID пользователя
            course_id: ID курса

        Returns:
            True если в избранном, False иначе
        """
        from sqlalchemy import exists

        return db.query(exists().where(
            Favorite.user_id == user_id,
            Favorite.course_id == course_id
        )).scalar()
