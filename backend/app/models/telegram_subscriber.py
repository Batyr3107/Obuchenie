from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from app.db.base import Base


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)"""
    return datetime.now(timezone.utc)


class TelegramSubscriber(Base):
    """Модель подписчиков Telegram бота"""
    __tablename__ = "telegram_subscribers"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    # Настройки подписки
    is_active = Column(Boolean, default=True)
    notify_new_courses = Column(Boolean, default=True)
    notify_top_courses = Column(Boolean, default=True)
    notify_special_offers = Column(Boolean, default=False)

    # Временные метки
    subscribed_at = Column(DateTime(timezone=True), default=utc_now)
    last_notified_at = Column(DateTime(timezone=True), nullable=True)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
