from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Unique constraint - один пользователь может добавить курс в избранное только один раз
    # PERFORMANCE: Composite index для оптимизации запросов
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='_user_course_favorite_uc'),
        Index('ix_favorite_user_created', 'user_id', 'created_at'),  # Для сортировки избранного пользователя по дате
    )

    # Relationships
    user = relationship("User", back_populates="favorites")
    course = relationship("Course", back_populates="favorites")
