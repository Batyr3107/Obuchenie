from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.base import get_db
from app.models.report import Report, ReportReason, ReportStatus
from app.models.review import Review
from app.models.user import User
from app.api.dependencies.auth import get_current_active_user

router = APIRouter()


class ReportCreate(BaseModel):
    review_id: int
    reason: ReportReason
    description: str = None


@router.post("/")
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Пожаловаться на отзыв"""

    # Проверить существование отзыва
    review = db.query(Review).filter(Review.id == report_data.review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Проверить, не жаловался ли уже
    existing = db.query(Report).filter(
        Report.user_id == current_user.id,
        Report.review_id == report_data.review_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="You have already reported this review")

    # Создать жалобу
    report = Report(
        user_id=current_user.id,
        review_id=report_data.review_id,
        reason=report_data.reason,
        description=report_data.description
    )

    db.add(report)
    db.commit()

    # Проверить количество жалоб на отзыв
    reports_count = db.query(Report).filter(
        Report.review_id == report_data.review_id,
        Report.status == ReportStatus.PENDING
    ).count()

    # Если >= 3 жалоб, отправить на модерацию
    if reports_count >= 3:
        review.is_approved = False

    db.commit()

    return {"message": "Report submitted successfully", "reports_count": reports_count}
