from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


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
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # На что жалоба
    review_id = Column(Integer, ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False)

    # Причина
    reason = Column(SQLEnum(ReportReason), nullable=False)
    description = Column(Text, nullable=True)

    # Статус
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="reports")
    review = relationship("Review", back_populates="reports")
