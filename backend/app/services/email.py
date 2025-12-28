"""
Email Module (Facade)

SRP: Этот модуль теперь служит фасадом для обратной совместимости.
Реальная логика разделена:
- email_templates.py - HTML шаблоны
- email_service.py - EmailService класс

Для новых проектов используйте:
    from app.services.email_service import email_service
    await email_service.send_welcome("user@example.com", "John")
"""
from typing import List, Optional

# Re-export from email_service for backward compatibility
from app.services.email_service import email_service

__all__ = [
    "send_welcome_email",
    "send_course_approved_email",
    "send_new_review_notification",
    "send_verification_email",
    "send_password_reset_email",
    "send_admin_notification",
    "email_service",
]


# ============ Backward-compatible functions ============
# These delegate to email_service singleton

async def send_welcome_email(email: str, name: str) -> bool:
    """
    Отправить приветственное письмо

    Deprecated: Use email_service.send_welcome() instead
    """
    return await email_service.send_welcome(email, name)


async def send_course_approved_email(email: str, course_title: str) -> bool:
    """
    Уведомление об одобрении курса

    Deprecated: Use email_service.send_course_approved() instead
    """
    return await email_service.send_course_approved(email, course_title)


async def send_new_review_notification(
    email: str,
    course_title: str,
    rating: float
) -> bool:
    """
    Уведомление о новом отзыве на курс

    Deprecated: Use email_service.send_new_review() instead
    """
    return await email_service.send_new_review(email, course_title, rating)


async def send_verification_email(email: str, verification_code: str) -> bool:
    """
    Отправить код верификации

    Deprecated: Use email_service.send_verification() instead
    """
    return await email_service.send_verification(email, verification_code)


async def send_password_reset_email(email: str, reset_token: str) -> bool:
    """
    Отправить ссылку для сброса пароля

    Deprecated: Use email_service.send_password_reset() instead
    """
    return await email_service.send_password_reset(email, reset_token)


async def send_admin_notification(
    subject: str,
    content: str,
    recipients: Optional[List[str]] = None
) -> bool:
    """
    Отправить уведомление админам

    Deprecated: Use email_service.send_admin_notification() instead
    """
    return await email_service.send_admin_notification(subject, content, recipients)
