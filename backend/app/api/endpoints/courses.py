from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from slugify import slugify

from app.db.base import get_db
from app.models.course import Course, CourseStatus
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseListItem
from app.api.dependencies.auth import get_current_active_user, get_current_admin

router = APIRouter()


@router.get("/", response_model=List[CourseListItem])
async def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    db: Session = Depends(get_db)
):
    """Получение списка курсов с фильтрацией"""

    query = db.query(Course).filter(Course.status == CourseStatus.APPROVED)

    # Фильтрация по категории
    if category_id:
        query = query.filter(Course.category_id == category_id)

    # Поиск по названию
    if search:
        query = query.filter(Course.title.ilike(f"%{search}%"))

    # Фильтрация по рейтингу
    if min_rating:
        query = query.filter(Course.avg_rating >= min_rating)

    # Сортировка по рейтингу (по умолчанию)
    query = query.order_by(Course.avg_rating.desc())

    courses = query.offset(skip).limit(limit).all()
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    """Получение детальной информации о курсе"""

    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Увеличение счетчика просмотров
    course.views_count += 1
    db.commit()

    return course


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Создание нового курса (требует модерации)"""

    # Создание slug из названия
    slug = slugify(course_data.title)

    # Проверка уникальности slug
    existing_course = db.query(Course).filter(Course.slug == slug).first()
    if existing_course:
        slug = f"{slug}-{course_data.category_id}"

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

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Обновление курса (только для админов)"""

    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Обновление полей
    update_data = course_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)

    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Удаление курса (только для админов)"""

    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    db.delete(course)
    db.commit()

    return None


@router.post("/{course_id}/approve", response_model=CourseResponse)
async def approve_course(
    course_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Одобрение курса (только для админов)"""

    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    course.status = CourseStatus.APPROVED
    db.commit()
    db.refresh(course)

    return course
