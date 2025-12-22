from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.base import get_db
from app.models.user import User
from app.models.review import Review
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseListItem
from app.schemas.review import ReviewResponse
from app.api.dependencies.auth import get_current_active_user, get_current_admin
from app.services.course_service import CourseService
from app.utils.json_helpers import batch_parse_json_fields

router = APIRouter()


@router.get("/", response_model=List[CourseListItem])
async def get_courses(
    skip: int = Query(0, ge=0, le=10000),  # SECURITY: Prevent excessive offset
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    db: Session = Depends(get_db)
):
    """
    Получение списка курсов с фильтрацией

    CLEAN CODE: Вся бизнес-логика в CourseService
    """
    courses = await CourseService.get_courses(
        db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        search=search,
        min_rating=min_rating
    )
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    """
    Получение детальной информации о курсе

    CLEAN CODE: Вся бизнес-логика в CourseService
    """
    course = await CourseService.get_course_by_id(db, course_id)

    # Увеличение счетчика просмотров
    CourseService.increment_views(db, course)

    return course


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Создание нового курса (требует модерации)

    CLEAN CODE: Вся бизнес-логика в CourseService
    """
    course = await CourseService.create_course(db, course_data)
    return course


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Обновление курса (только для админов)

    CLEAN CODE: Вся бизнес-логика в CourseService
    """
    course = await CourseService.update_course(db, course_id, course_data)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Удаление курса (только для админов)

    CLEAN CODE: Вся бизнес-логика в CourseService
    """
    await CourseService.delete_course(db, course_id)
    return None


@router.post("/{course_id}/approve", response_model=CourseResponse)
async def approve_course(
    course_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Одобрение курса (только для админов)

    CLEAN CODE: Вся бизнес-логика в CourseService
    """
    course = await CourseService.approve_course(db, course_id)
    return course


@router.get("/{course_id}/reviews", response_model=List[ReviewResponse])
async def get_course_reviews(
    course_id: int,
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(10, ge=1, le=50, description="Max reviews to return"),
    sort: str = Query("recent", regex="^(recent|helpful|rating_high|rating_low)$"),
    db: Session = Depends(get_db)
):
    """
    Получение отзывов курса с пагинацией.

    PERFORMANCE: Returns paginated reviews instead of loading all reviews.
    Use this instead of loading reviews from course detail endpoint.

    Args:
        course_id: ID курса
        skip: Number of reviews to skip (for pagination)
        limit: Max reviews to return (default 10, max 50)
        sort: Sort order - recent, helpful, rating_high, rating_low

    Returns:
        List of paginated reviews
    """
    # Verify course exists
    await CourseService.get_course_by_id(db, course_id)

    # Build query
    query = db.query(Review).filter(
        Review.course_id == course_id,
        Review.is_approved == True
    )

    # Apply sorting
    if sort == "recent":
        query = query.order_by(Review.created_at.desc())
    elif sort == "helpful":
        query = query.order_by(Review.helpful_votes.desc())
    elif sort == "rating_high":
        query = query.order_by(Review.rating.desc())
    elif sort == "rating_low":
        query = query.order_by(Review.rating.asc())

    reviews = query.offset(skip).limit(limit).all()

    # Parse JSON fields
    batch_parse_json_fields(reviews, ['pros', 'cons'])

    return reviews
