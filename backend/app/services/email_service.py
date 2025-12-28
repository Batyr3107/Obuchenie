"""
Email Service Module

SRP: Отвечает только за отправку email
DIP: Реализует IEmailSender protocol
OCP: Шаблоны вынесены в email_templates.py

Usage:
    from app.services.email_service import email_service

    await email_service.send_welcome("user@example.com", "John")
    await email_service.send("user@example.com", "Subject", "<p>Body</p>")
"""
from typing import List, Optional, Protocol
import logging
import asyncio
from smtplib import SMTPException

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from app.core.config import settings
from app.services.email_templates import EmailTemplates, get_subject

logger = logging.getLogger(__name__)


class IEmailSender(Protocol):
    """Protocol for email sender (DIP)"""

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        is_html: bool = True
    ) -> bool:
        """Send email"""
        ...


class EmailService:
    """
    Email service implementing IEmailSender.

    SOLID:
    - SRP: Only handles email sending
    - OCP: Templates in separate module
    - DIP: Implements IEmailSender protocol
    """

    def __init__(
        self,
        config: Optional[ConnectionConfig] = None,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize email service.

        Args:
            config: FastMail config (uses default if None)
            max_retries: Max retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        if config is None:
            config = ConnectionConfig(
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

        self._mail = FastMail(config)

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        is_html: bool = True
    ) -> bool:
        """
        Send email with retry logic.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body (HTML or plain text)
            is_html: Whether body is HTML

        Returns:
            True if sent successfully
        """
        message = MessageSchema(
            subject=subject,
            recipients=[to],
            body=body,
            subtype="html" if is_html else "plain"
        )

        return await self._send_with_retry(message)

    async def send_to_many(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        is_html: bool = True
    ) -> bool:
        """Send email to multiple recipients"""
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype="html" if is_html else "plain"
        )

        return await self._send_with_retry(message)

    async def _send_with_retry(self, message: MessageSchema) -> bool:
        """Send with retry logic"""
        for attempt in range(self.max_retries):
            try:
                await self._mail.send_message(message)
                logger.info(f"Email sent to {message.recipients}")
                return True

            except SMTPException as e:
                logger.error(f"SMTP error: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    return False

            except (ConnectionRefusedError, OSError, TimeoutError) as e:
                logger.error(f"Connection error: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    return False

            except ValueError as e:
                logger.error(f"Validation error: {e}")
                return False  # Don't retry validation errors

            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    return False

        return False

    # ============ Convenience methods using templates ============

    async def send_welcome(self, email: str, name: str) -> bool:
        """Send welcome email"""
        return await self.send(
            to=email,
            subject=get_subject("welcome"),
            body=EmailTemplates.welcome(name)
        )

    async def send_course_approved(self, email: str, course_title: str) -> bool:
        """Send course approved notification"""
        return await self.send(
            to=email,
            subject=get_subject("course_approved", course_title=course_title),
            body=EmailTemplates.course_approved(course_title)
        )

    async def send_new_review(
        self,
        email: str,
        course_title: str,
        rating: float
    ) -> bool:
        """Send new review notification"""
        return await self.send(
            to=email,
            subject=get_subject("new_review", course_title=course_title),
            body=EmailTemplates.new_review(course_title, rating)
        )

    async def send_verification(self, email: str, code: str) -> bool:
        """Send verification code"""
        return await self.send(
            to=email,
            subject=get_subject("verification"),
            body=EmailTemplates.verification_code(code)
        )

    async def send_password_reset(self, email: str, token: str) -> bool:
        """Send password reset link"""
        reset_link = f"https://courserate.com/reset-password?token={token}"
        return await self.send(
            to=email,
            subject=get_subject("password_reset"),
            body=EmailTemplates.password_reset(reset_link)
        )

    async def send_admin_notification(
        self,
        subject: str,
        content: str,
        recipients: Optional[List[str]] = None
    ) -> bool:
        """Send notification to admins"""
        if not recipients:
            recipients = [settings.FIRST_SUPERUSER_EMAIL]

        return await self.send_to_many(
            recipients=recipients,
            subject=get_subject("admin", subject=subject),
            body=EmailTemplates.admin_notification(content)
        )


# Global instance (singleton pattern)
email_service = EmailService()
