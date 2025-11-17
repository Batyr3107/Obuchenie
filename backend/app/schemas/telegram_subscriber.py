from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TelegramSubscriberBase(BaseModel):
    """Базовая схема подписчика"""
    telegram_user_id: int = Field(..., description="Telegram user ID")
    username: Optional[str] = Field(None, description="Telegram username")
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")


class TelegramSubscriberCreate(TelegramSubscriberBase):
    """Схема для создания подписчика"""
    notify_new_courses: bool = Field(True, description="Уведомления о новых курсах")
    notify_top_courses: bool = Field(True, description="Уведомления о топ курсах")
    notify_special_offers: bool = Field(False, description="Уведомления о спец. предложениях")


class TelegramSubscriberUpdate(BaseModel):
    """Схема для обновления подписчика"""
    is_active: Optional[bool] = None
    notify_new_courses: Optional[bool] = None
    notify_top_courses: Optional[bool] = None
    notify_special_offers: Optional[bool] = None


class TelegramSubscriberResponse(TelegramSubscriberBase):
    """Схема ответа с информацией о подписчике"""
    id: int
    is_active: bool
    notify_new_courses: bool
    notify_top_courses: bool
    notify_special_offers: bool
    subscribed_at: datetime
    last_notified_at: Optional[datetime]
    unsubscribed_at: Optional[datetime]

    class Config:
        from_attributes = True
