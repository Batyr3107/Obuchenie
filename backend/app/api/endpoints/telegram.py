"""
API endpoints для Telegram бота
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime

from app.api.dependencies.auth import get_current_active_user, get_current_admin_user
from app.api.dependencies.database import get_db
from app.models.telegram_subscriber import TelegramSubscriber
from app.models.user import User
from app.schemas.telegram_subscriber import (
    TelegramSubscriberCreate,
    TelegramSubscriberUpdate,
    TelegramSubscriberResponse
)

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/subscribe", response_model=TelegramSubscriberResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_telegram(
    subscriber_data: TelegramSubscriberCreate,
    db: Session = Depends(get_db)
):
    """
    Подписаться на уведомления от Telegram бота
    """
    # Проверяем, существует ли подписчик
    existing = db.query(TelegramSubscriber).filter(
        TelegramSubscriber.telegram_user_id == subscriber_data.telegram_user_id
    ).first()

    if existing:
        # Если подписчик уже существует, но был отписан - активируем снова
        if not existing.is_active:
            existing.is_active = True
            existing.subscribed_at = datetime.utcnow()
            existing.unsubscribed_at = None
            existing.notify_new_courses = subscriber_data.notify_new_courses
            existing.notify_top_courses = subscriber_data.notify_top_courses
            existing.notify_special_offers = subscriber_data.notify_special_offers
            db.commit()
            db.refresh(existing)
            return existing
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Подписка уже активна"
            )

    # Создаем нового подписчика
    try:
        db_subscriber = TelegramSubscriber(
            telegram_user_id=subscriber_data.telegram_user_id,
            username=subscriber_data.username,
            first_name=subscriber_data.first_name,
            last_name=subscriber_data.last_name,
            is_active=True,
            notify_new_courses=subscriber_data.notify_new_courses,
            notify_top_courses=subscriber_data.notify_top_courses,
            notify_special_offers=subscriber_data.notify_special_offers
        )
        db.add(db_subscriber)
        db.commit()
        db.refresh(db_subscriber)
        return db_subscriber
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка создания подписки"
        )


@router.post("/unsubscribe/{telegram_user_id}", status_code=status.HTTP_200_OK)
async def unsubscribe_telegram(
    telegram_user_id: int,
    db: Session = Depends(get_db)
):
    """
    Отписаться от уведомлений Telegram бота
    """
    subscriber = db.query(TelegramSubscriber).filter(
        TelegramSubscriber.telegram_user_id == telegram_user_id
    ).first()

    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )

    subscriber.is_active = False
    subscriber.unsubscribed_at = datetime.utcnow()
    db.commit()

    return {"message": "Подписка отменена"}


@router.get("/subscriber/{telegram_user_id}", response_model=TelegramSubscriberResponse)
async def get_subscriber(
    telegram_user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить информацию о подписчике
    """
    subscriber = db.query(TelegramSubscriber).filter(
        TelegramSubscriber.telegram_user_id == telegram_user_id
    ).first()

    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписчик не найден"
        )

    return subscriber


@router.patch("/subscriber/{telegram_user_id}", response_model=TelegramSubscriberResponse)
async def update_subscriber(
    telegram_user_id: int,
    update_data: TelegramSubscriberUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить настройки подписки
    """
    subscriber = db.query(TelegramSubscriber).filter(
        TelegramSubscriber.telegram_user_id == telegram_user_id
    ).first()

    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписчик не найден"
        )

    # Обновляем только переданные поля
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(subscriber, field, value)

    db.commit()
    db.refresh(subscriber)
    return subscriber


# Admin endpoints
@router.get("/admin/subscribers", response_model=List[TelegramSubscriberResponse])
async def get_all_subscribers(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить список всех подписчиков (только для админов)
    """
    query = db.query(TelegramSubscriber)

    if active_only:
        query = query.filter(TelegramSubscriber.is_active == True)

    subscribers = query.offset(skip).limit(limit).all()
    return subscribers


@router.get("/admin/subscribers/stats")
async def get_subscribers_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получить статистику подписчиков (только для админов)
    """
    total = db.query(TelegramSubscriber).count()
    active = db.query(TelegramSubscriber).filter(TelegramSubscriber.is_active == True).count()
    inactive = total - active

    return {
        "total_subscribers": total,
        "active_subscribers": active,
        "inactive_subscribers": inactive
    }
