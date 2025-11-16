from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.db.base import get_db
from app.models.course import Course, CourseStatus

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

    courses = db.query(Course).filter(
        Course.status == CourseStatus.APPROVED,
        Course.title.ilike(f"%{q}%")
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

    return suggestions


@router.get("/popular")
async def get_popular_searches(db: Session = Depends(get_db)):
    """Популярные поисковые запросы (топ курсы)"""

    popular_courses = db.query(Course).filter(
        Course.status == CourseStatus.APPROVED
    ).order_by(
        Course.views_count.desc()
    ).limit(10).all()

    return [
        {"title": course.title, "id": course.id}
        for course in popular_courses
    ]
