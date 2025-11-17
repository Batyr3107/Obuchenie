"""
Report Service

ARCHITECTURE: Бизнес-логика для работы с жалобами на отзывы
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.report import Report, ReportStatus, ReportReason
from app.models.review import Review
from app.schemas.report import ReportCreate
from app.utils.db_helpers import get_or_404


class ReportService:
    """Сервис для работы с жалобами"""

    @staticmethod
    async def create_report(
        db: Session,
        report_data: ReportCreate,
        user_id: int
    ) -> Report:
        """
        Создание жалобы на отзыв

        Args:
            db: Database session
            report_data: Данные жалобы
            user_id: ID пользователя, создающего жалобу

        Returns:
            Созданная жалоба

        Raises:
            HTTPException: 404 если отзыв не найден
            HTTPException: 409 если жалоба уже существует
        """
        from fastapi import HTTPException, status

        # Проверка существования отзыва
        review = get_or_404(db, Review, report_data.review_id, "Review not found")

        # Проверка дубликата жалобы
        existing = db.query(Report).filter(
            Report.review_id == report_data.review_id,
            Report.user_id == user_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already reported this review"
            )

        # Создание жалобы
        new_report = Report(
            review_id=report_data.review_id,
            user_id=user_id,
            reason=report_data.reason,
            comment=report_data.comment,
            status=ReportStatus.PENDING
        )

        db.add(new_report)

        try:
            db.commit()
            db.refresh(new_report)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Report already exists"
            )

        return new_report

    @staticmethod
    async def get_reports_count(db: Session, review_id: int) -> int:
        """
        Получение количества жалоб на отзыв

        Args:
            db: Database session
            review_id: ID отзыва

        Returns:
            Количество жалоб
        """
        reports_count = db.query(Report).filter(
            Report.review_id == review_id,
            Report.status == ReportStatus.PENDING
        ).count()

        return reports_count

    @staticmethod
    async def get_user_reports(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> list:
        """
        Получение жалоб пользователя

        Args:
            db: Database session
            user_id: ID пользователя
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            Список жалоб пользователя
        """
        reports = db.query(Report).filter(
            Report.user_id == user_id
        ).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

        return reports
