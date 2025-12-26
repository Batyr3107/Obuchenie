from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import logging

from app.db.base import get_db

logger = logging.getLogger(__name__)
from app.models.user import User, UserRole
from app.schemas.user import UserResponse
from app.schemas.course import CourseResponse
from app.api.dependencies.auth import get_current_admin
from app.services.stats_service import StatsService
from app.services.admin_service import AdminService

router = APIRouter()


# ============ МОДЕРАЦИЯ КУРСОВ ============

@router.get("/courses/pending", response_model=List[CourseResponse])
async def get_pending_courses(
    skip: int = Query(0, ge=0, le=10000),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Получить курсы ожидающие модерации

    CLEAN CODE: Вся логика в AdminService
    """
    courses = await AdminService.get_pending_courses(db, skip, limit)
    return courses


@router.post("/courses/{course_id}/approve", response_model=CourseResponse)
async def approve_course(
    course_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Одобрить курс

    CLEAN CODE: Вся логика в AdminService
    """
    try:
        course = await AdminService.approve_course(db, course_id)
        return course
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to approve course")
        raise HTTPException(status_code=500, detail="Failed to approve course")


@router.post("/courses/{course_id}/reject", response_model=CourseResponse)
async def reject_course(
    course_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Отклонить курс

    CLEAN CODE: Вся логика в AdminService
    """
    course = await AdminService.reject_course(db, course_id)
    return course


# ============ УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ============

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0, le=10000),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Получить список всех пользователей

    CLEAN CODE: Вся логика в AdminService
    """
    users = await AdminService.get_users(db, skip, limit, search, role)
    return users


@router.post("/users/{user_id}/block")
async def block_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Заблокировать пользователя

    CLEAN CODE: Вся логика в AdminService
    """
    try:
        result = await AdminService.block_user(db, user_id)
        return result
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to block user")
        raise HTTPException(status_code=500, detail="Failed to block user")


@router.post("/users/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Разблокировать пользователя

    CLEAN CODE: Вся логика в AdminService
    """
    result = await AdminService.unblock_user(db, user_id)
    return result


@router.post("/users/{user_id}/role")
async def change_user_role(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Изменить роль пользователя

    CLEAN CODE: Вся логика в AdminService
    """
    result = await AdminService.change_user_role(db, user_id, new_role)
    return result


# ============ МОДЕРАЦИЯ ОТЗЫВОВ ============

@router.get("/reviews/reported")
async def get_reported_reviews(
    skip: int = Query(0, ge=0, le=10000),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Получить отзывы с жалобами

    CLEAN CODE: Вся логика в AdminService
    PERFORMANCE: Используем joinedload для предотвращения N+1 queries
    """
    review_reports = await AdminService.get_reported_reviews(db, skip, limit)
    return review_reports


@router.post("/reviews/{review_id}/block")
async def block_review(
    review_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Заблокировать отзыв

    CLEAN CODE: Вся логика в AdminService
    """
    try:
        result = await AdminService.block_review(db, review_id)
        return result
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to block review")
        raise HTTPException(status_code=500, detail="Failed to block review")


@router.post("/reports/{report_id}/resolve")
async def resolve_report(
    report_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Отклонить жалобу (отзыв нормальный)

    CLEAN CODE: Вся логика в AdminService
    """
    result = await AdminService.resolve_report(db, report_id)
    return result


# ============ СТАТИСТИКА ============

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Получить общую статистику платформы

    CLEAN CODE: Вся логика в StatsService
    PERFORMANCE: 4 оптимизированных запроса вместо 8
    """
    stats = await StatsService.get_admin_stats(db)
    return stats
