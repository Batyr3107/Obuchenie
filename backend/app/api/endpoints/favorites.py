from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.models.favorite import Favorite
from app.models.course import Course
from app.models.user import User
from app.schemas.course import CourseListItem
from app.api.dependencies.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[CourseListItem])
async def get_favorites(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить список избранных курсов"""
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()

    course_ids = [fav.course_id for fav in favorites]
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all()

    return courses


@router.post("/{course_id}")
async def add_to_favorites(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Добавить курс в избранное"""

    # Проверить существование курса
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Проверить, не добавлен ли уже
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.course_id == course_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Course already in favorites")

    # Добавить в избранное
    favorite = Favorite(
        user_id=current_user.id,
        course_id=course_id
    )

    db.add(favorite)

    # Увеличить счетчик избранного у курса
    course.favorites_count += 1

    db.commit()

    return {"message": "Course added to favorites"}


@router.delete("/{course_id}")
async def remove_from_favorites(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удалить курс из избранного"""

    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.course_id == course_id
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    # Уменьшить счетчик
    course = db.query(Course).filter(Course.id == course_id).first()
    if course and course.favorites_count > 0:
        course.favorites_count -= 1

    db.delete(favorite)
    db.commit()

    return {"message": "Course removed from favorites"}


@router.get("/check/{course_id}")
async def check_favorite(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Проверить, в избранном ли курс"""

    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.course_id == course_id
    ).first()

    return {"is_favorite": favorite is not None}
