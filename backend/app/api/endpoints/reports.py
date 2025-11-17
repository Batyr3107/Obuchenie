from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.api.dependencies.auth import get_current_active_user
from app.schemas.report import ReportCreate
from app.services.report_service import ReportService

router = APIRouter()


@router.post("/")
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Пожаловаться на отзыв

    CLEAN CODE: Вся логика в ReportService
    """
    # CLEAN CODE: Используем ReportService вместо прямого db.query
    report = await ReportService.create_report(db, report_data, current_user.id)

    # Получить количество жалоб на этот отзыв
    reports_count = await ReportService.get_reports_count(db, report_data.review_id)

    return {
        "message": "Report submitted successfully",
        "reports_count": reports_count,
        "report_id": report.id
    }
