from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.db.base import get_db
from app.models.review import Review
from app.models.course import Course
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.api.dependencies.auth import get_current_active_user
from app.core.config import settings

router = APIRouter()


def calculate_overall_rating(review_data: ReviewCreate) -> float:
    """Вычисление общего рейтинга"""
    return round((
        review_data.content_quality +
        review_data.instructors +
        review_data.support +
        review_data.price_quality +
        review_data.practical
    ) / 5, 2)


def update_course_ratings(course: Course, db: Session):
    """Обновление рейтингов курса"""
    reviews = db.query(Review).filter(
        Review.course_id == course.id,
        Review.is_approved == True
    ).all()

    if not reviews:
        course.avg_rating = 0.0
        course.total_reviews = 0
        course.avg_content_quality = 0.0
        course.avg_instructors = 0.0
        course.avg_support = 0.0
        course.avg_price_quality = 0.0
        course.avg_practical = 0.0
        return

    total = len(reviews)
    course.total_reviews = total

    course.avg_content_quality = round(sum(r.content_quality for r in reviews) / total, 2)
    course.avg_instructors = round(sum(r.instructors for r in reviews) / total, 2)
    course.avg_support = round(sum(r.support for r in reviews) / total, 2)
    course.avg_price_quality = round(sum(r.price_quality for r in reviews) / total, 2)
    course.avg_practical = round(sum(r.practical for r in reviews) / total, 2)

    course.avg_rating = round((
        course.avg_content_quality +
        course.avg_instructors +
        course.avg_support +
        course.avg_price_quality +
        course.avg_practical
    ) / 5, 2)


@router.get("/", response_model=List[ReviewResponse])
async def get_reviews(
    course_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Получение списка отзывов"""

    query = db.query(Review).filter(Review.is_approved == True)

    if course_id:
        query = query.filter(Review.course_id == course_id)

    reviews = query.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()

    # Конвертация JSON строк обратно в списки
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


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Создание нового отзыва"""

    # Проверка существования курса
    course = db.query(Course).filter(Course.id == review_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Проверка, не оставлял ли пользователь уже отзыв на этот курс
    existing_review = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.course_id == review_data.course_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this course"
        )

    # Проверка лимита отзывов в день
    today = datetime.utcnow().date()
    reviews_today = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.created_at >= datetime.combine(today, datetime.min.time())
    ).count()

    if reviews_today >= settings.REVIEWS_PER_DAY_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily review limit ({settings.REVIEWS_PER_DAY_LIMIT}) exceeded"
        )

    # Проверка возраста аккаунта
    account_age = (datetime.utcnow() - current_user.created_at).days
    if account_age < settings.ACCOUNT_MIN_AGE_DAYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account must be at least {settings.ACCOUNT_MIN_AGE_DAYS} days old to leave reviews"
        )

    # Вычисление общего рейтинга
    overall_rating = calculate_overall_rating(review_data)

    # Конвертация списков в JSON строки
    pros_json = json.dumps(review_data.pros) if review_data.pros else None
    cons_json = json.dumps(review_data.cons) if review_data.cons else None

    # Создание отзыва
    new_review = Review(
        user_id=current_user.id,
        course_id=review_data.course_id,
        content_quality=review_data.content_quality,
        instructors=review_data.instructors,
        support=review_data.support,
        price_quality=review_data.price_quality,
        practical=review_data.practical,
        overall_rating=overall_rating,
        review_text=review_data.review_text,
        pros=pros_json,
        cons=cons_json,
        recommend=review_data.recommend,
        completion_status=review_data.completion_status,
        completion_date=review_data.completion_date
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    # Обновление рейтингов курса
    update_course_ratings(course, db)
    db.commit()

    # Конвертация обратно для ответа
    if new_review.pros:
        new_review.pros = json.loads(new_review.pros)
    if new_review.cons:
        new_review.cons = json.loads(new_review.cons)

    return new_review


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление отзыва"""

    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    # Проверка, что пользователь - автор отзыва
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own reviews"
        )

    # Проверка, что прошло не менее 30 дней с последнего изменения
    if review.last_edited_at:
        days_since_edit = (datetime.utcnow() - review.last_edited_at).days
        if days_since_edit < 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You can edit your review again in {30 - days_since_edit} days"
            )

    # Обновление полей
    update_data = review_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field in ['pros', 'cons'] and value is not None:
            value = json.dumps(value)
        setattr(review, field, value)

    # Пересчет общего рейтинга если изменились оценки
    if any(hasattr(review_data, f) and getattr(review_data, f) is not None
           for f in ['content_quality', 'instructors', 'support', 'price_quality', 'practical']):
        review.overall_rating = round((
            review.content_quality +
            review.instructors +
            review.support +
            review.price_quality +
            review.practical
        ) / 5, 2)

    review.last_edited_at = datetime.utcnow()
    db.commit()
    db.refresh(review)

    # Обновление рейтингов курса
    course = db.query(Course).filter(Course.id == review.course_id).first()
    update_course_ratings(course, db)
    db.commit()

    # Конвертация обратно
    if review.pros:
        review.pros = json.loads(review.pros)
    if review.cons:
        review.cons = json.loads(review.cons)

    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удаление отзыва"""

    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    # Проверка прав
    from app.models.user import UserRole
    if review.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )

    course_id = review.course_id
    db.delete(review)
    db.commit()

    # Обновление рейтингов курса
    course = db.query(Course).filter(Course.id == course_id).first()
    if course:
        update_course_ratings(course, db)
        db.commit()

    return None
