from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
from app.core.constants import EmailSettings
from typing import List, Optional
import logging
import asyncio
from smtplib import SMTPException

logger = logging.getLogger(__name__)


# Email конфигурация
# FIXED: Используем правильные атрибуты из settings (SMTP_* вместо MAIL_*)
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=settings.SMTP_TLS,
    MAIL_SSL_TLS=settings.SMTP_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fm = FastMail(conf)


def _wrap_email_template(title: str, content: str) -> str:
    """
    Обертка HTML шаблона для email

    DRY: Единый базовый шаблон для всех писем

    Args:
        title: Заголовок письма
        content: HTML контент письма

    Returns:
        Полный HTML шаблон
    """
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0ea5e9;">{title}</h2>
                {content}
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #666; font-size: 14px;">С уважением,<br>Команда CourseRate</p>
            </div>
        </body>
    </html>
    """


def _create_email_message(subject: str, recipients: List[str], content: str, title: str) -> MessageSchema:
    """
    Создание объекта email сообщения

    DRY: Единая точка создания MessageSchema

    Args:
        subject: Тема письма
        recipients: Список получателей
        content: HTML контент (без обертки)
        title: Заголовок в теле письма

    Returns:
        MessageSchema объект
    """
    return MessageSchema(
        subject=subject,
        recipients=recipients,
        body=_wrap_email_template(title, content),
        subtype="html"
    )


async def send_email_with_retry(
    message: MessageSchema,
    max_retries: int = EmailSettings.MAX_RETRIES,
    retry_delay: int = EmailSettings.RETRY_DELAY
) -> bool:
    """
    Отправка email с повторными попытками и обработкой ошибок

    Args:
        message: Схема сообщения для отправки
        max_retries: Максимальное количество попыток
        retry_delay: Задержка между попытками в секундах

    Returns:
        bool: True если отправка успешна, False в противном случае
    """
    for attempt in range(max_retries):
        try:
            await fm.send_message(message)
            logger.info(f"Email успешно отправлен на {message.recipients}")
            return True

        except SMTPException as e:
            logger.error(f"SMTP ошибка при отправке email на {message.recipients}: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Повторная попытка {attempt + 2}/{max_retries} через {retry_delay}с...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Не удалось отправить email после {max_retries} попыток")
                return False

        except (ConnectionRefusedError, OSError, TimeoutError) as e:
            logger.error(f"Ошибка подключения при отправке email: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                return False

        except ValueError as e:
            # Ошибки валидации email адреса
            logger.error(f"Ошибка валидации при отправке email: {str(e)}")
            return False  # Не retry при ошибках валидации

        except Exception as e:
            # JUSTIFICATION: Email service не должен ронять приложение
            # Логируем и возвращаем False для graceful degradation
            logger.error(f"Неожиданная ошибка при отправке email: {str(e)}", exc_info=True)
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                return False

    return False


async def send_welcome_email(email: str, name: str) -> bool:
    """Отправить приветственное письмо"""
    content = f"""
        <p>Привет, {name}!</p>
        <p>Спасибо за регистрацию на платформе CourseRate.</p>
        <p>Теперь вы можете:</p>
        <ul>
            <li>Оставлять отзывы на курсы</li>
            <li>Добавлять новые курсы</li>
            <li>Сохранять курсы в избранное</li>
        </ul>
    """
    message = _create_email_message(
        subject="Добро пожаловать в CourseRate!",
        recipients=[email],
        content=content,
        title="Добро пожаловать в CourseRate!"
    )
    return await send_email_with_retry(message)


async def send_course_approved_email(email: str, course_title: str) -> bool:
    """Уведомление об одобрении курса"""
    content = f"""
        <p>Отличные новости!</p>
        <p>Ваш курс "<strong>{course_title}</strong>" был одобрен модератором и теперь доступен на платформе.</p>
        <p>Пользователи уже могут просматривать его и оставлять отзывы.</p>
    """
    message = _create_email_message(
        subject=f"Курс '{course_title}' одобрен!",
        recipients=[email],
        content=content,
        title="Ваш курс одобрен!"
    )
    return await send_email_with_retry(message)


async def send_new_review_notification(email: str, course_title: str, rating: float) -> bool:
    """Уведомление о новом отзыве на курс"""
    content = f"""
        <p>На курс "<strong>{course_title}</strong>" был оставлен новый отзыв.</p>
        <p>Оценка: <strong>{rating}/5</strong></p>
        <p>Войдите на платформу, чтобы посмотреть детали.</p>
    """
    message = _create_email_message(
        subject=f"Новый отзыв на '{course_title}'",
        recipients=[email],
        content=content,
        title="Новый отзыв на ваш курс!"
    )
    return await send_email_with_retry(message)


async def send_verification_email(email: str, verification_code: str) -> bool:
    """Отправить код верификации"""
    content = f"""
        <p>Ваш код подтверждения:</p>
        <h1 style="color: #0ea5e9; text-align: center;">{verification_code}</h1>
        <p>Введите этот код на сайте для подтверждения вашего email.</p>
        <p>Код действителен 30 минут.</p>
    """
    message = _create_email_message(
        subject="Подтверждение email - CourseRate",
        recipients=[email],
        content=content,
        title="Подтверждение email"
    )
    return await send_email_with_retry(message)


async def send_password_reset_email(email: str, reset_token: str) -> bool:
    """Отправить ссылку для сброса пароля"""
    reset_link = f"https://courserate.com/reset-password?token={reset_token}"
    content = f"""
        <p>Вы запросили сброс пароля.</p>
        <p>Нажмите на кнопку ниже, чтобы сбросить пароль:</p>
        <p style="text-align: center;">
            <a href="{reset_link}" style="display: inline-block; padding: 12px 24px; background-color: #0ea5e9; color: white; text-decoration: none; border-radius: 6px;">
                Сбросить пароль
            </a>
        </p>
        <p>Или скопируйте эту ссылку в браузер:</p>
        <p style="word-break: break-all;">{reset_link}</p>
        <p>Ссылка действительна 1 час.</p>
        <p><em>Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.</em></p>
    """
    message = _create_email_message(
        subject="Сброс пароля - CourseRate",
        recipients=[email],
        content=content,
        title="Сброс пароля"
    )
    return await send_email_with_retry(message)


async def send_admin_notification(
    subject: str,
    content: str,
    recipients: Optional[List[str]] = None
) -> bool:
    """Отправить уведомление админам"""
    if not recipients:
        recipients = [settings.FIRST_SUPERUSER_EMAIL]

    message = _create_email_message(
        subject=f"[ADMIN] {subject}",
        recipients=recipients,
        content=content,
        title="Уведомление администратора"
    )
    return await send_email_with_retry(message)
