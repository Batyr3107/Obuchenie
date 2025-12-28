"""
Email Templates Module

SRP: Отвечает только за HTML шаблоны писем
OCP: Добавление нового шаблона не требует изменения других модулей

Шаблоны используют str.format() для простоты.
Для сложных шаблонов рекомендуется Jinja2.
"""
from typing import Dict, Any


class EmailTemplates:
    """Коллекция email шаблонов"""

    # Base template wrapper
    BASE_TEMPLATE = """
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            {content}
            <p style="margin-top: 30px; color: #666;">
                С уважением,<br>
                <strong>Команда CourseRate</strong>
            </p>
        </body>
    </html>
    """

    @classmethod
    def _wrap(cls, content: str) -> str:
        """Wrap content in base template"""
        return cls.BASE_TEMPLATE.format(content=content)

    @classmethod
    def welcome(cls, name: str) -> str:
        """Приветственное письмо"""
        content = f"""
            <h2 style="color: #0ea5e9;">Добро пожаловать в CourseRate!</h2>
            <p>Привет, <strong>{name}</strong>!</p>
            <p>Спасибо за регистрацию на платформе CourseRate.</p>
            <p>Теперь вы можете:</p>
            <ul>
                <li>Оставлять отзывы на курсы</li>
                <li>Добавлять новые курсы</li>
                <li>Сохранять курсы в избранное</li>
            </ul>
        """
        return cls._wrap(content)

    @classmethod
    def course_approved(cls, course_title: str) -> str:
        """Уведомление об одобрении курса"""
        content = f"""
            <h2 style="color: #22c55e;">Ваш курс одобрен!</h2>
            <p>Отличные новости!</p>
            <p>Ваш курс "<strong>{course_title}</strong>" был одобрен модератором
               и теперь доступен на платформе.</p>
            <p>Пользователи уже могут просматривать его и оставлять отзывы.</p>
        """
        return cls._wrap(content)

    @classmethod
    def new_review(cls, course_title: str, rating: float) -> str:
        """Уведомление о новом отзыве"""
        content = f"""
            <h2 style="color: #0ea5e9;">Новый отзыв на ваш курс!</h2>
            <p>На курс "<strong>{course_title}</strong>" был оставлен новый отзыв.</p>
            <p>Оценка: <strong style="color: #f59e0b;">{rating}/5</strong></p>
            <p>Войдите на платформу, чтобы посмотреть детали.</p>
        """
        return cls._wrap(content)

    @classmethod
    def verification_code(cls, code: str) -> str:
        """Код верификации email"""
        content = f"""
            <h2 style="color: #0ea5e9;">Подтверждение email</h2>
            <p>Ваш код подтверждения:</p>
            <h1 style="color: #0ea5e9; font-size: 36px; letter-spacing: 5px;
                       background: #f0f9ff; padding: 20px; text-align: center;
                       border-radius: 8px;">{code}</h1>
            <p>Введите этот код на сайте для подтверждения вашего email.</p>
            <p style="color: #666;">Код действителен 30 минут.</p>
        """
        return cls._wrap(content)

    @classmethod
    def password_reset(cls, reset_link: str) -> str:
        """Сброс пароля"""
        content = f"""
            <h2 style="color: #0ea5e9;">Сброс пароля</h2>
            <p>Вы запросили сброс пароля.</p>
            <p>Нажмите на кнопку ниже, чтобы сбросить пароль:</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}"
                   style="display: inline-block; padding: 14px 28px;
                          background-color: #0ea5e9; color: white;
                          text-decoration: none; border-radius: 8px;
                          font-weight: bold;">
                    Сбросить пароль
                </a>
            </p>
            <p>Или скопируйте эту ссылку в браузер:</p>
            <p style="background: #f5f5f5; padding: 10px; border-radius: 4px;
                      word-break: break-all;">{reset_link}</p>
            <p style="color: #666;">Ссылка действительна 1 час.</p>
            <p style="color: #999; font-size: 12px;">
                Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.
            </p>
        """
        return cls._wrap(content)

    @classmethod
    def admin_notification(cls, content_html: str) -> str:
        """Уведомление для админов"""
        content = f"""
            <h2 style="color: #dc2626;">Уведомление администратора</h2>
            <div style="background: #fef2f2; padding: 15px; border-radius: 8px;
                        border-left: 4px solid #dc2626;">
                {content_html}
            </div>
        """
        return cls._wrap(content)


# OCP: Email subjects dictionary - add new subjects here
EMAIL_SUBJECTS: Dict[str, str] = {
    "welcome": "Добро пожаловать в CourseRate!",
    "course_approved": "Курс '{course_title}' одобрен!",
    "new_review": "Новый отзыв на '{course_title}'",
    "verification": "Подтверждение email - CourseRate",
    "password_reset": "Сброс пароля - CourseRate",
    "admin": "[ADMIN] {subject}",
}


def get_subject(template_name: str, **kwargs) -> str:
    """
    Get formatted subject for email template.

    Args:
        template_name: Name of template
        **kwargs: Format arguments

    Returns:
        Formatted subject string
    """
    subject_template = EMAIL_SUBJECTS.get(template_name, template_name)
    return subject_template.format(**kwargs) if kwargs else subject_template
