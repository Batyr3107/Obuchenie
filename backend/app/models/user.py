from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.base import Base


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)"""
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    USER = "user"
    COURSE_OWNER = "course_owner"
    ADMIN = "admin"


class UserLevel(str, enum.Enum):
    NEWBIE = "newbie"
    EXPERIENCED = "experienced"
    EXPERT = "expert"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)

    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    level = Column(SQLEnum(UserLevel), default=UserLevel.NEWBIE, nullable=False)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)

    reputation_score = Column(Integer, default=0)
    helpful_votes = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
