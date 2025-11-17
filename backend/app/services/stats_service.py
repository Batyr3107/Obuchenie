"""
Stats Service

PERFORMANCE: Оптимизированные SQL запросы для статистики
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.user import User
from app.models.course import Course, CourseStatus
from app.models.review import Review
from app.models.report import Report, ReportStatus


class StatsService:
    """Сервис для получения статистики"""

    @staticmethod
    async def get_admin_stats(db: Session) -> dict:
        """
        Получить полную статистику платформы

        PERFORMANCE: Оптимизированные запросы с SQL aggregation
        Вместо 8 отдельных запросов - 4 оптимизированных
        """
        return {
            "users": await StatsService._get_user_stats(db),
            "courses": await StatsService._get_course_stats(db),
            "reviews": await StatsService._get_review_stats(db),
            "reports": await StatsService._get_report_stats(db),
        }

    @staticmethod
    async def _get_user_stats(db: Session) -> dict:
        """
        Статистика пользователей

        PERFORMANCE: Один запрос вместо трех
        """
        stats = db.query(
            func.count(User.id).label('total'),
            func.sum(case((User.is_active == True, 1), else_=0)).label('active'),
            func.sum(case((User.is_blocked == True, 1), else_=0)).label('blocked'),
        ).first()

        return {
            "total": stats.total or 0,
            "active": stats.active or 0,
            "blocked": stats.blocked or 0,
        }

    @staticmethod
    async def _get_course_stats(db: Session) -> dict:
        """
        Статистика курсов

        PERFORMANCE: Один запрос вместо четырех
        """
        stats = db.query(
            func.count(Course.id).label('total'),
            func.sum(case((Course.status == CourseStatus.APPROVED, 1), else_=0)).label('approved'),
            func.sum(case((Course.status == CourseStatus.PENDING, 1), else_=0)).label('pending'),
            func.sum(case((Course.status == CourseStatus.REJECTED, 1), else_=0)).label('rejected'),
        ).first()

        return {
            "total": stats.total or 0,
            "approved": stats.approved or 0,
            "pending": stats.pending or 0,
            "rejected": stats.rejected or 0,
        }

    @staticmethod
    async def _get_review_stats(db: Session) -> dict:
        """
        Статистика отзывов

        PERFORMANCE: Один запрос вместо трех
        """
        stats = db.query(
            func.count(Review.id).label('total'),
            func.sum(case((Review.is_approved == True, 1), else_=0)).label('approved'),
            func.sum(case((Review.is_blocked == True, 1), else_=0)).label('blocked'),
        ).first()

        return {
            "total": stats.total or 0,
            "approved": stats.approved or 0,
            "blocked": stats.blocked or 0,
        }

    @staticmethod
    async def _get_report_stats(db: Session) -> dict:
        """
        Статистика жалоб

        PERFORMANCE: Один запрос вместо двух
        """
        stats = db.query(
            func.count(Report.id).label('total'),
            func.sum(case((Report.status == ReportStatus.PENDING, 1), else_=0)).label('pending'),
        ).first()

        return {
            "total": stats.total or 0,
            "pending": stats.pending or 0,
        }
