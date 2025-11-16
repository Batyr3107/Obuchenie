from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class CompletionStatus(str, enum.Enum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    NOT_FINISHED = "not_finished"


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    # Связи
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)

    # Оценки по критериям (1-5)
    content_quality = Column(Float, nullable=False)  # Качество материала
    instructors = Column(Float, nullable=False)      # Преподаватели
    support = Column(Float, nullable=False)          # Поддержка
    price_quality = Column(Float, nullable=False)    # Цена/качество
    practical = Column(Float, nullable=False)        # Практическая польза

    # Общая оценка (среднее)
    overall_rating = Column(Float, nullable=False)

    # Текст отзыва
    review_text = Column(Text, nullable=False)
    pros = Column(Text, nullable=True)  # JSON list
    cons = Column(Text, nullable=True)  # JSON list

    # Дополнительная информация
    recommend = Column(Boolean, default=True)
    completion_status = Column(SQLEnum(CompletionStatus), nullable=False)
    completion_date = Column(String(7), nullable=True)  # YYYY-MM

    # Статистика
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)

    # Статус
    is_approved = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_edited_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="reviews")
    course = relationship("Course", back_populates="reviews")
    reports = relationship("Report", back_populates="review", cascade="all, delete-orphan")
