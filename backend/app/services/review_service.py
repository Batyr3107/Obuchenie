"""
Review Service - бизнес-логика для работы с отзывами

ARCHITECTURE: Вынесена вся бизнес-логика из endpoints
для улучшения тестируемости и поддерживаемости
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import json

from app.models.review import Review, CompletionStatus
from app.models.course import Course
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.core.config import settings
from fastapi import HTTPException, status


class ReviewService:
    """Сервис для управления отзывами"""

    @staticmethod
    def calculate_overall_rating(review_data: ReviewCreate) -> float:
        """Вычисление общего рейтинга из 5 критериев"""
        return round((
            review_data.content_quality +
            review_data.instructors +
            review_data.support +
            review_data.price_quality +
            review_data.practical
        ) / 5, 2)

    @staticmethod
    async def validate_review_creation(
        db: Session,
        course_id: int,
        user_id: int
    ) -> Course:
        """
        Валидация возможности создания отзыва

        Returns:
            Course: Курс, на который оставляется отзыв

        Raises:
            HTTPException: Если валидация не прошла
        """
        # Проверка существования курса
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Проверка дубликата отзыва
        existing_review = db.query(Review).filter(
            Review.user_id == user_id,
            Review.course_id == course_id
        ).first()

        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this course"
            )

        return course

    @staticmethod
    async def check_rate_limit(db: Session, user_id: int) -> None:
        """
        Проверка лимита отзывов в день

        PERFORMANCE: Uses limit() to stop counting once we exceed the limit,
        instead of counting all reviews for the day.

        Raises:
            HTTPException: Если лимит превышен
        """
        today = datetime.now(timezone.utc).date()
        # PERFORMANCE: Only fetch up to limit to check if exceeded
        reviews_count = db.query(Review.id).filter(
            Review.user_id == user_id,
            func.date(Review.created_at) == today
        ).limit(settings.REVIEWS_PER_DAY_LIMIT).count()

        if reviews_count >= settings.REVIEWS_PER_DAY_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily review limit ({settings.REVIEWS_PER_DAY_LIMIT}) exceeded. Try again tomorrow."
            )

    @staticmethod
    def create_review_instance(
        review_data: ReviewCreate,
        user_id: int,
        overall_rating: float
    ) -> Review:
        """Создание экземпляра отзыва"""
        return Review(
            user_id=user_id,
            course_id=review_data.course_id,
            content_quality=review_data.content_quality,
            instructors=review_data.instructors,
            support=review_data.support,
            price_quality=review_data.price_quality,
            practical=review_data.practical,
            overall_rating=overall_rating,
            review_text=review_data.review_text,
            pros=json.dumps(review_data.pros) if review_data.pros else None,
            cons=json.dumps(review_data.cons) if review_data.cons else None,
            recommend=review_data.recommend,
            completion_status=review_data.completion_status,
            completion_date=review_data.completion_date
        )

    @staticmethod
    def update_course_ratings(course: Course, db: Session) -> None:
        """
        Обновление рейтингов курса на основе всех одобренных отзывов

        PERFORMANCE: Используем SQL aggregation вместо Python loops
        """
        stats = db.query(
            func.count(Review.id).label('total'),
            func.avg(Review.content_quality).label('avg_content_quality'),
            func.avg(Review.instructors).label('avg_instructors'),
            func.avg(Review.support).label('avg_support'),
            func.avg(Review.price_quality).label('avg_price_quality'),
            func.avg(Review.practical).label('avg_practical'),
        ).filter(
            Review.course_id == course.id,
            Review.is_approved == True
        ).first()

        if stats.total == 0 or stats.total is None:
            course.avg_rating = 0.0
            course.total_reviews = 0
            course.avg_content_quality = 0.0
            course.avg_instructors = 0.0
            course.avg_support = 0.0
            course.avg_price_quality = 0.0
            course.avg_practical = 0.0
            return

        course.total_reviews = stats.total
        course.avg_content_quality = round(float(stats.avg_content_quality or 0), 2)
        course.avg_instructors = round(float(stats.avg_instructors or 0), 2)
        course.avg_support = round(float(stats.avg_support or 0), 2)
        course.avg_price_quality = round(float(stats.avg_price_quality or 0), 2)
        course.avg_practical = round(float(stats.avg_practical or 0), 2)

        course.avg_rating = round((
            course.avg_content_quality +
            course.avg_instructors +
            course.avg_support +
            course.avg_price_quality +
            course.avg_practical
        ) / 5, 2)

    @staticmethod
    async def create_review(
        db: Session,
        review_data: ReviewCreate,
        user: User
    ) -> Review:
        """
        Полный процесс создания отзыва

        Args:
            db: Database session
            review_data: Данные отзыва
            user: Текущий пользователь

        Returns:
            Review: Созданный отзыв

        Raises:
            HTTPException: При ошибках валидации или создания
        """
        # Валидация
        course = await ReviewService.validate_review_creation(
            db, review_data.course_id, user.id
        )

        # Проверка лимита
        await ReviewService.check_rate_limit(db, user.id)

        # Вычисление рейтинга
        overall_rating = ReviewService.calculate_overall_rating(review_data)

        # Создание отзыва
        new_review = ReviewService.create_review_instance(
            review_data, user.id, overall_rating
        )

        try:
            db.add(new_review)
            db.commit()
            db.refresh(new_review)

            # Обновление рейтингов курса
            ReviewService.update_course_ratings(course, db)
            db.commit()

            return new_review

        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Review already exists or constraint violation"
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create review: {str(e)}"
            )

    @staticmethod
    async def update_review(
        db: Session,
        review_id: int,
        review_data: ReviewUpdate,
        user_id: int
    ) -> Review:
        """
        Обновление отзыва

        Returns:
            Review: Обновленный отзыв

        Raises:
            HTTPException: Если отзыв не найден или нет прав
        """
        review = db.query(Review).filter(Review.id == review_id).first()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own reviews"
            )

        # Обновление полей
        update_data = review_data.model_dump(exclude_unset=True)

        # Обработка списков pros/cons
        if 'pros' in update_data and update_data['pros'] is not None:
            update_data['pros'] = json.dumps(update_data['pros'])
        if 'cons' in update_data and update_data['cons'] is not None:
            update_data['cons'] = json.dumps(update_data['cons'])

        for field, value in update_data.items():
            setattr(review, field, value)

        # Пересчет overall_rating если изменились критерии
        criteria_changed = any(
            field in update_data for field in
            ['content_quality', 'instructors', 'support', 'price_quality', 'practical']
        )

        if criteria_changed:
            review.overall_rating = round((
                review.content_quality +
                review.instructors +
                review.support +
                review.price_quality +
                review.practical
            ) / 5, 2)

        review.last_edited_at = datetime.now(timezone.utc)

        try:
            db.commit()
            db.refresh(review)

            # Обновление рейтингов курса
            course = db.query(Course).filter(Course.id == review.course_id).first()
            if course:
                ReviewService.update_course_ratings(course, db)
                db.commit()

            return review

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update review: {str(e)}"
            )

    @staticmethod
    async def delete_review(
        db: Session,
        review_id: int,
        user_id: int
    ) -> None:
        """
        Удаление отзыва

        Raises:
            HTTPException: Если отзыв не найден или нет прав
        """
        review = db.query(Review).filter(Review.id == review_id).first()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews"
            )

        course_id = review.course_id

        try:
            db.delete(review)
            db.commit()

            # Обновление рейтингов курса
            course = db.query(Course).filter(Course.id == course_id).first()
            if course:
                ReviewService.update_course_ratings(course, db)
                db.commit()

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete review: {str(e)}"
            )

    @staticmethod
    def parse_json_fields(reviews: List[Review]) -> List[Review]:
        """Конвертация JSON строк в списки для pros/cons"""
        for review in reviews:
            if review.pros:
                try:
                    review.pros = json.loads(review.pros)
                except:
                    review.pros = []
            if review.cons:
                try:
                    review.cons = json.loads(review.cons)
                except:
                    review.cons = []
        return reviews
