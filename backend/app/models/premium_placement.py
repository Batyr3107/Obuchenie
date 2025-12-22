from sqlalchemy import Column, Integer, DateTime, Enum as SQLEnum, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.base import Base


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)"""
    return datetime.now(timezone.utc)


class PlacementTier(str, enum.Enum):
    BASIC = "basic"
    FEATURED = "featured"  # Выделенное
    TOP = "top"            # Топ-размещение


class PremiumPlacement(Base):
    __tablename__ = "premium_placements"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), unique=True, nullable=False)

    tier = Column(SQLEnum(PlacementTier), nullable=False)
    is_active = Column(Boolean, default=True)

    # Цена и оплата
    monthly_price = Column(Float, nullable=False)

    # Период действия
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    # Статистика (для TOP размещения)
    views_count = Column(Integer, default=0)
    clicks_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="premium_placement")
