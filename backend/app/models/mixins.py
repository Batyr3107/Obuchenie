"""
Mixins для моделей SQLAlchemy

Best Practice: Use timezone-aware datetimes for proper timestamp handling
"""
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Boolean, Integer
from sqlalchemy.orm import Query
from typing import Optional


def utc_now() -> datetime:
    """Helper function for timezone-aware UTC timestamps."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """
    Mixin для добавления timestamps (created_at, updated_at)

    Best Practice: Use timezone-aware UTC timestamps
    """
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class SoftDeleteMixin:
    """
    Mixin для soft delete (мягкое удаление)

    Добавляет поля:
    - deleted_at: DateTime когда запись была удалена
    - is_deleted: Boolean флаг удаления

    Использование:
        class MyModel(Base, SoftDeleteMixin):
            __tablename__ = "my_table"
            id = Column(Integer, primary_key=True)

        # Мягкое удаление
        obj.soft_delete()

        # Восстановление
        obj.restore()

        # Запрос только неудаленных
        query = session.query(MyModel).filter(MyModel.is_deleted == False)

        # Или использовать scope
        MyModel.active()  # только активные
        MyModel.deleted()  # только удаленные
        MyModel.with_deleted()  # все записи
    """
    deleted_at: Optional[DateTime] = Column(DateTime, nullable=True, index=True)
    is_deleted: bool = Column(Boolean, default=False, nullable=False, index=True)

    def soft_delete(self) -> None:
        """Мягкое удаление записи"""
        self.deleted_at = datetime.now(timezone.utc)
        self.is_deleted = True

    def restore(self) -> None:
        """Восстановление удаленной записи"""
        self.deleted_at = None
        self.is_deleted = False

    @property
    def is_active(self) -> bool:
        """Проверка активности записи"""
        return not self.is_deleted

    @classmethod
    def active(cls, query: Query) -> Query:
        """Фильтр только активных (неудаленных) записей"""
        return query.filter(cls.is_deleted == False)

    @classmethod
    def deleted(cls, query: Query) -> Query:
        """Фильтр только удаленных записей"""
        return query.filter(cls.is_deleted == True)

    @classmethod
    def with_deleted(cls, query: Query) -> Query:
        """Все записи (включая удаленные)"""
        return query


class AuditMixin(TimestampMixin):
    """
    Mixin для аудита изменений

    Включает:
    - created_at, updated_at (из TimestampMixin)
    - created_by_id, updated_by_id
    """
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)


class FullAuditMixin(TimestampMixin, SoftDeleteMixin):
    """
    Полный аудит: timestamps + soft delete + user tracking

    Комбинирует:
    - created_at, updated_at
    - deleted_at, is_deleted
    - created_by_id, updated_by_id, deleted_by_id
    """
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    deleted_by_id = Column(Integer, nullable=True)

    def soft_delete(self, user_id: Optional[int] = None) -> None:
        """Мягкое удаление с отслеживанием пользователя"""
        super().soft_delete()
        if user_id:
            self.deleted_by_id = user_id


# Примеры использования:

"""
# 1. Базовая модель с timestamps
class Course(Base, TimestampMixin):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    # created_at и updated_at добавятся автоматически


# 2. Модель с soft delete
class Review(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    text = Column(Text)

# Использование:
review = session.query(Review).first()
review.soft_delete()  # Помечается как удаленный
session.commit()

# Запросы
active_reviews = session.query(Review).filter(Review.is_deleted == False).all()
# или
active_reviews = Review.active(session.query(Review)).all()


# 3. Полный аудит
class ImportantData(Base, FullAuditMixin):
    __tablename__ = "important_data"
    id = Column(Integer, primary_key=True)
    data = Column(String(255))

# Использование:
data = session.query(ImportantData).first()
data.soft_delete(user_id=current_user.id)
session.commit()

# Все изменения теперь отслеживаются:
# - Кто создал (created_by_id)
# - Кто обновил (updated_by_id)
# - Кто удалил (deleted_by_id)
# - Когда (created_at, updated_at, deleted_at)
"""
