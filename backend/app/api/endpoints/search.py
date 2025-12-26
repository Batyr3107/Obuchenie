from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.db.base import get_db
from app.core.cache import cache_manager
from app.core.constants import CacheTimeout
from app.services.search_service import SearchService

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
    """
    Автодополнение поиска

    CLEAN CODE: Вся логика в SearchService
    PERFORMANCE: Кэшируем результаты на 5 минут
    """
    # PERFORMANCE: Кэшируем результаты автокомплита на 5 минут
    cache_key = f"autocomplete:{q}:{limit}"
    cached_suggestions = cache_manager.get(cache_key)

    if cached_suggestions is not None:
        return cached_suggestions

    # CLEAN CODE: Используем SearchService вместо прямого db.query
    courses = await SearchService.autocomplete(db, q, limit)

    suggestions = [
        SearchSuggestion(
            id=course["id"],
            title=course["title"],
            type="course"
        )
        for course in courses
    ]

    # Сохраняем в кэш
    cache_manager.set(cache_key, suggestions, expire=CacheTimeout.SEARCH)

    return suggestions


@router.get("/popular")
async def get_popular_searches(db: Session = Depends(get_db)):
    """
    Популярные поисковые запросы (топ курсы)

    CLEAN CODE: Вся логика в SearchService
    PERFORMANCE: Кэшируем популярные поиски на 30 минут
    """
    # PERFORMANCE: Кэшируем популярные поиски на 30 минут
    cache_key = "popular_searches"
    cached_popular = cache_manager.get(cache_key)

    if cached_popular is not None:
        return cached_popular

    # CLEAN CODE: Используем SearchService вместо прямого db.query
    popular_courses = await SearchService.get_popular_courses(db, limit=10)

    result = [
        {"title": course.title, "id": course.id}
        for course in popular_courses
    ]

    # Сохраняем в кэш
    cache_manager.set(cache_key, result, expire=CacheTimeout.THIRTY_MINUTES)

    return result
