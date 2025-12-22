from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.base import Base


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)"""
    return datetime.now(timezone.utc)


class ReportReason(str, enum.Enum):
    SPAM = "spam"
    OFFENSIVE = "offensive"
    FAKE = "fake"
    INAPPROPRIATE = "inappropriate"
    OTHER = "other"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    # Кто сообщил
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # На что жалоба
    review_id = Column(Integer, ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False, index=True)

    # Причина
    reason = Column(SQLEnum(ReportReason), nullable=False)
    description = Column(Text, nullable=True)

    # Статус
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING, index=True)

    # Временные метки
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # PERFORMANCE: Composite index для оптимизации админ-запросов
    __table_args__ = (
        Index('ix_report_status_created', 'status', 'created_at'),  # Для фильтрации по статусу и сортировки по дате
    )

    # Relationships
    user = relationship("User", back_populates="reports")
    review = relationship("Review", back_populates="reports")
