"""
Reviews API Endpoints

REFACTORED: Вынесена вся бизнес-логика в ReviewService
для улучшения читаемости, тестируемости и поддерживаемости
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.base import get_db
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.api.dependencies.auth import get_current_active_user
from app.services.review_service import ReviewService
from app.utils.json_helpers import batch_parse_json_fields
from app.core.rate_limit import limiter

router = APIRouter()


@router.get("/", response_model=List[ReviewResponse])
async def get_reviews(
    course_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Получение списка отзывов с фильтрацией

    CLEAN CODE: Короткий, читаемый endpoint всего ~15 строк
    """
    query = db.query(Review).filter(Review.is_approved == True)

    if course_id:
        query = query.filter(Review.course_id == course_id)

    reviews = query.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()

    # Конвертация JSON строк в списки
    batch_parse_json_fields(reviews, ['pros', 'cons'])

    return reviews


@router.post("/", response_model=ReviewResponse, status_code=201)
@limiter.limit("5/day")  # Max 5 reviews per day per user
async def create_review(
    request: Request,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Создание нового отзыва

    CLEAN CODE: Вся бизнес-логика в ReviewService
    Endpoint всего ~10 строк вместо 95!
    """
    review = await ReviewService.create_review(db, review_data, current_user)

    # Конвертация JSON для ответа
    batch_parse_json_fields([review], ['pros', 'cons'])

    return review


@router.put("/{review_id}", response_model=ReviewResponse)
@limiter.limit("10/hour")  # Max 10 updates per hour
async def update_review(
    request: Request,
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновление отзыва

    CLEAN CODE: Простой endpoint, логика в сервисе
    """
    review = await ReviewService.update_review(db, review_id, review_data, current_user.id)

    # Конвертация JSON для ответа
    batch_parse_json_fields([review], ['pros', 'cons'])

    return review


@router.delete("/{review_id}", status_code=204)
@limiter.limit("10/hour")  # Max 10 deletes per hour
async def delete_review(
    request: Request,
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Удаление отзыва

    CLEAN CODE: Минимальный код в endpoint
    """
    await ReviewService.delete_review(db, review_id, current_user.id)
    return None
