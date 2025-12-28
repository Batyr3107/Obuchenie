"""
Review Moderator Service

SRP: Отвечает только за модерацию отзывов
ISP: Минимальный интерфейс для модерации отзывов
"""
from typing import List
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload

from app.models.review import Review
from app.models.report import Report, ReportStatus
from app.utils.db_helpers import get_or_404


class ReviewModeratorService:
    """Сервис для модерации отзывов"""

    @staticmethod
    async def get_reported_reviews(
        db: Session,
        skip: int = 0,
        limit: int = 20
    ) -> List[dict]:
        """
        Получение отзывов с жалобами

        PERFORMANCE: Использует joinedload для предотвращения N+1 queries

        Args:
            db: Database session
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            Список отзывов с жалобами
        """
        reports = db.query(Report).options(
            joinedload(Report.review).joinedload(Review.user),
            joinedload(Report.review).joinedload(Review.course),
            joinedload(Report.user)
        ).filter(
            Report.status == ReportStatus.PENDING
        ).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

        # Группировка по отзывам
        review_reports = {}
        for report in reports:
            if report.review_id not in review_reports:
                review_reports[report.review_id] = {
                    "review": report.review,
                    "reports": []
                }
            review_reports[report.review_id]["reports"].append(report)

        return list(review_reports.values())

    @staticmethod
    async def block_review(db: Session, review_id: int) -> dict:
        """
        Блокировка отзыва

        TRANSACTIONAL: Атомарная операция с обновлением всех связанных жалоб

        Args:
            db: Database session
            review_id: ID отзыва

        Returns:
            Сообщение об успехе

        Raises:
            HTTPException: 404 если отзыв не найден
        """
        review = get_or_404(db, Review, review_id, "Review not found")

        review.is_blocked = True
        review.is_approved = False

        # Обновить статус всех жалоб на этот отзыв
        db.query(Report).filter(Report.review_id == review_id).update({
            "status": ReportStatus.RESOLVED,
            "resolved_at": datetime.now(timezone.utc)
        })

        db.commit()

        return {"message": "Review blocked successfully"}

    @staticmethod
    async def resolve_report(db: Session, report_id: int) -> dict:
        """
        Отклонение жалобы (отзыв нормальный)

        Args:
            db: Database session
            report_id: ID жалобы

        Returns:
            Сообщение об успехе

        Raises:
            HTTPException: 404 если жалоба не найдена
        """
        report = get_or_404(db, Report, report_id, "Report not found")
        report.status = ReportStatus.REJECTED
        report.resolved_at = datetime.now(timezone.utc)
        db.commit()

        return {"message": "Report rejected"}
