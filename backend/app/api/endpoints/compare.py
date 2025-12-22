from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.db.base import get_db
from app.models.course import Course
from app.schemas.course import CourseResponse

router = APIRouter()


@router.get("/", response_model=List[CourseResponse])
async def compare_courses(
    course_ids: str = Query(..., max_length=100, description="Comma-separated course IDs (e.g., 1,2,3)"),
    db: Session = Depends(get_db)
):
    """Сравнить курсы"""

    try:
        ids = [int(id.strip()) for id in course_ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course IDs format")

    if len(ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 courses required for comparison")

    if len(ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 courses can be compared")

    # PERFORMANCE: Получить курсы с joinedload для предотвращения N+1
    courses = db.query(Course).options(
        joinedload(Course.category),
        joinedload(Course.subcategory),
        joinedload(Course.tags)
    ).filter(Course.id.in_(ids)).all()

    if len(courses) != len(ids):
        raise HTTPException(status_code=404, detail="Some courses not found")

    return courses
