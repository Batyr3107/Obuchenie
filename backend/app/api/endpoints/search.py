from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.db.base import get_db
from app.models.course import Course, CourseStatus
from app.core.validators import validate_search_query
from app.core.cache import cache_manager

router = APIRouter()


class SearchSuggestion(BaseModel):
    id: int
    title: str
    type: str = "course"


@router.get("/autocomplete", response_model=List[SearchSuggestion])
async def autocomplete_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Автодополнение поиска"""

    # Валидация поискового запроса
    validated_query = validate_search_query(q)

    # PERFORMANCE: Кэшируем результаты автокомплита на 5 минут
    cache_key = f"autocomplete:{validated_query}:{limit}"
    cached_suggestions = cache_manager.get(cache_key)

    if cached_suggestions is not None:
        return cached_suggestions

    courses = db.query(Course).filter(
        Course.status == CourseStatus.APPROVED,
        Course.title.ilike(f"%{validated_query}%")
    ).order_by(
        Course.avg_rating.desc()
    ).limit(limit).all()

    suggestions = [
        SearchSuggestion(
            id=course.id,
            title=course.title,
            type="course"
        )
        for course in courses
    ]

    # Сохраняем в кэш на 5 минут (300 секунд)
    cache_manager.set(cache_key, suggestions, expire=300)

    return suggestions


@router.get("/popular")
async def get_popular_searches(db: Session = Depends(get_db)):
    """Популярные поисковые запросы (топ курсы)"""
    # PERFORMANCE: Кэшируем популярные поиски на 30 минут
    cache_key = "popular_searches"
    cached_popular = cache_manager.get(cache_key)

    if cached_popular is not None:
        return cached_popular

    popular_courses = db.query(Course).filter(
        Course.status == CourseStatus.APPROVED
    ).order_by(
        Course.views_count.desc()
    ).limit(10).all()

    result = [
        {"title": course.title, "id": course.id}
        for course in popular_courses
    ]

    # Сохраняем в кэш на 30 минут (1800 секунд)
    cache_manager.set(cache_key, result, expire=1800)

    return result
