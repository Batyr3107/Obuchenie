from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.base import get_db
from app.models.course import Course, CourseStatus
from app.models.user import User, UserRole
from app.models.review import Review
from app.models.report import Report, ReportStatus
from app.schemas.user import UserResponse
from app.schemas.course import CourseResponse
from app.api.dependencies.auth import get_current_admin

router = APIRouter()


# ============ МОДЕРАЦИЯ КУРСОВ ============

@router.get("/courses/pending", response_model=List[CourseResponse])
async def get_pending_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Получить курсы ожидающие модерации"""
    courses = db.query(Course).filter(
        Course.status == CourseStatus.PENDING
    ).order_by(Course.created_at.desc()).offset(skip).limit(limit).all()

    return courses


@router.post("/courses/{course_id}/approve", response_model=CourseResponse)
async def approve_course(
    course_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Одобрить курс"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.status = CourseStatus.APPROVED
    db.commit()
    db.refresh(course)

    return course


@router.post("/courses/{course_id}/reject", response_model=CourseResponse)
async def reject_course(
    course_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Отклонить курс"""
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.status = CourseStatus.REJECTED
    db.commit()
    db.refresh(course)

    return course


# ============ УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ============

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Получить список всех пользователей"""
    query = db.query(User)

    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )

    if role:
        query = query.filter(User.role == role)

    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users


@router.post("/users/{user_id}/block")
async def block_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Заблокировать пользователя"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Cannot block admin")

    user.is_blocked = True
    db.commit()

    return {"message": "User blocked successfully"}


@router.post("/users/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Разблокировать пользователя"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_blocked = False
    db.commit()

    return {"message": "User unblocked successfully"}


@router.post("/users/{user_id}/role")
async def change_user_role(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Изменить роль пользователя"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = new_role
    db.commit()

    return {"message": f"User role changed to {new_role}"}


# ============ МОДЕРАЦИЯ ОТЗЫВОВ ============

@router.get("/reviews/reported")
async def get_reported_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Получить отзывы с жалобами"""
    reports = db.query(Report).filter(
        Report.status == ReportStatus.PENDING
    ).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

    # Группировка по отзывам
    review_reports = {}
    for report in reports:
        if report.review_id not in review_reports:
            review_reports[report.review_id] = {
                "review": db.query(Review).filter(Review.id == report.review_id).first(),
                "reports": []
            }
        review_reports[report.review_id]["reports"].append(report)

    return list(review_reports.values())


@router.post("/reviews/{review_id}/block")
async def block_review(
    review_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Заблокировать отзыв"""
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.is_blocked = True
    review.is_approved = False

    # Обновить статус всех жалоб на этот отзыв
    db.query(Report).filter(Report.review_id == review_id).update({
        "status": ReportStatus.RESOLVED,
        "resolved_at": datetime.utcnow()
    })

    db.commit()

    return {"message": "Review blocked successfully"}


@router.post("/reports/{report_id}/resolve")
async def resolve_report(
    report_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Отклонить жалобу (отзыв нормальный)"""
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = ReportStatus.REJECTED
    report.resolved_at = datetime.utcnow()
    db.commit()

    return {"message": "Report rejected"}


# ============ СТАТИСТИКА ============

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Получить общую статистику платформы"""

    stats = {
        "users": {
            "total": db.query(User).count(),
            "active": db.query(User).filter(User.is_active == True).count(),
            "blocked": db.query(User).filter(User.is_blocked == True).count(),
        },
        "courses": {
            "total": db.query(Course).count(),
            "approved": db.query(Course).filter(Course.status == CourseStatus.APPROVED).count(),
            "pending": db.query(Course).filter(Course.status == CourseStatus.PENDING).count(),
            "rejected": db.query(Course).filter(Course.status == CourseStatus.REJECTED).count(),
        },
        "reviews": {
            "total": db.query(Review).count(),
            "approved": db.query(Review).filter(Review.is_approved == True).count(),
            "blocked": db.query(Review).filter(Review.is_blocked == True).count(),
        },
        "reports": {
            "total": db.query(Report).count(),
            "pending": db.query(Report).filter(Report.status == ReportStatus.PENDING).count(),
        }
    }

    return stats
