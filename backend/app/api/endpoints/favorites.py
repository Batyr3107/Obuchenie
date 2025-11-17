from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.models.user import User
from app.schemas.course import CourseListItem
from app.api.dependencies.auth import get_current_active_user
from app.services.favorite_service import FavoriteService

router = APIRouter()


@router.get("/", response_model=List[CourseListItem])
async def get_favorites(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получить список избранных курсов

    CLEAN CODE: Вся бизнес-логика в FavoriteService
    """
    favorites = await FavoriteService.get_user_favorites(db, current_user.id)
    courses = [fav.course for fav in favorites]
    return courses


@router.post("/{course_id}")
async def add_to_favorites(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Добавить курс в избранное

    CLEAN CODE: Вся бизнес-логика в FavoriteService
    """
    await FavoriteService.add_to_favorites(db, current_user.id, course_id)
    return {"message": "Course added to favorites"}


@router.delete("/{course_id}")
async def remove_from_favorites(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Удалить курс из избранного

    CLEAN CODE: Вся бизнес-логика в FavoriteService
    """
    await FavoriteService.remove_from_favorites(db, current_user.id, course_id)
    return {"message": "Course removed from favorites"}


@router.get("/check/{course_id}")
async def check_favorite(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Проверить, в избранном ли курс

    CLEAN CODE: Вся бизнес-логика в FavoriteService
    """
    is_favorite = await FavoriteService.is_favorite(db, current_user.id, course_id)
    return {"is_favorite": is_favorite}
