from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
from typing import List


# Email конфигурация
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_TLS,
    MAIL_SSL_TLS=settings.MAIL_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fm = FastMail(conf)


async def send_welcome_email(email: str, name: str):
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

    await fm.send_message(message)


async def send_course_approved_email(email: str, course_title: str):
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

    await fm.send_message(message)


async def send_new_review_notification(email: str, course_title: str, rating: float):
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

    await fm.send_message(message)


async def send_verification_email(email: str, verification_code: str):
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

    await fm.send_message(message)


async def send_password_reset_email(email: str, reset_token: str):
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

    await fm.send_message(message)


async def send_admin_notification(
    subject: str,
    content: str,
    recipients: List[str] = None
):
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

    await fm.send_message(message)
