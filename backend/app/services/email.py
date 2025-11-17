from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
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


async def send_email_with_retry(
    message: MessageSchema,
    max_retries: int = 3,
    retry_delay: int = 2
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
    html = f"""
    <html>
        <body>
            <h2>Добро пожаловать в CourseRate!</h2>
            <p>Привет, {name}!</p>
            <p>Спасибо за регистрацию на платформе CourseRate.</p>
            <p>Теперь вы можете:</p>
            <ul>
                <li>Оставлять отзывы на курсы</li>
                <li>Добавлять новые курсы</li>
                <li>Сохранять курсы в избранное</li>
            </ul>
            <p>С уважением,<br>Команда CourseRate</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="Добро пожаловать в CourseRate!",
        recipients=[email],
        body=html,
        subtype="html"
    )

    return await send_email_with_retry(message)


async def send_course_approved_email(email: str, course_title: str) -> bool:
    """Уведомление об одобрении курса"""
    html = f"""
    <html>
        <body>
            <h2>Ваш курс одобрен!</h2>
            <p>Отличные новости!</p>
            <p>Ваш курс "<strong>{course_title}</strong>" был одобрен модератором и теперь доступен на платформе.</p>
            <p>Пользователи уже могут просматривать его и оставлять отзывы.</p>
            <p>С уважением,<br>Команда CourseRate</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject=f"Курс '{course_title}' одобрен!",
        recipients=[email],
        body=html,
        subtype="html"
    )

    return await send_email_with_retry(message)


async def send_new_review_notification(email: str, course_title: str, rating: float) -> bool:
    """Уведомление о новом отзыве на курс"""
    html = f"""
    <html>
        <body>
            <h2>Новый отзыв на ваш курс!</h2>
            <p>На курс "<strong>{course_title}</strong>" был оставлен новый отзыв.</p>
            <p>Оценка: <strong>{rating}/5</strong></p>
            <p>Войдите на платформу, чтобы посмотреть детали.</p>
            <p>С уважением,<br>Команда CourseRate</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject=f"Новый отзыв на '{course_title}'",
        recipients=[email],
        body=html,
        subtype="html"
    )

    return await send_email_with_retry(message)


async def send_verification_email(email: str, verification_code: str) -> bool:
    """Отправить код верификации"""
    html = f"""
    <html>
        <body>
            <h2>Подтверждение email</h2>
            <p>Ваш код подтверждения:</p>
            <h1 style="color: #0ea5e9;">{verification_code}</h1>
            <p>Введите этот код на сайте для подтверждения вашего email.</p>
            <p>Код действителен 30 минут.</p>
            <p>С уважением,<br>Команда CourseRate</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="Подтверждение email - CourseRate",
        recipients=[email],
        body=html,
        subtype="html"
    )

    return await send_email_with_retry(message)


async def send_password_reset_email(email: str, reset_token: str) -> bool:
    """Отправить ссылку для сброса пароля"""
    reset_link = f"https://courserate.com/reset-password?token={reset_token}"

    html = f"""
    <html>
        <body>
            <h2>Сброс пароля</h2>
            <p>Вы запросили сброс пароля.</p>
            <p>Нажмите на кнопку ниже, чтобы сбросить пароль:</p>
            <a href="{reset_link}" style="display: inline-block; padding: 12px 24px; background-color: #0ea5e9; color: white; text-decoration: none; border-radius: 6px;">
                Сбросить пароль
            </a>
            <p>Или скопируйте эту ссылку в браузер:</p>
            <p>{reset_link}</p>
            <p>Ссылка действительна 1 час.</p>
            <p>Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.</p>
            <p>С уважением,<br>Команда CourseRate</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="Сброс пароля - CourseRate",
        recipients=[email],
        body=html,
        subtype="html"
    )

    return await send_email_with_retry(message)


async def send_admin_notification(
    subject: str,
    content: str,
    recipients: List[str] = None
) -> bool:
    """Отправить уведомление админам"""
    if not recipients:
        recipients = [settings.FIRST_SUPERUSER_EMAIL]

    html = f"""
    <html>
        <body>
            <h2>Уведомление админа</h2>
            {content}
            <p>С уважением,<br>Система CourseRate</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject=f"[ADMIN] {subject}",
        recipients=recipients,
        body=html,
        subtype="html"
    )

    return await send_email_with_retry(message)
