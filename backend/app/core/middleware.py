"""
Middleware для логирования и мониторинга

OBSERVABILITY: Structured logging with correlation IDs for distributed tracing
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
import uuid
import contextvars

# Context variable for request ID - accessible anywhere in the request lifecycle
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar('request_id', default='')

logger = logging.getLogger(__name__)


class CorrelationIDFilter(logging.Filter):
    """
    Logging filter that adds correlation_id to all log records.

    OBSERVABILITY: Enables tracing requests across all log entries.
    Add this filter to your handlers to include correlation_id in logs.
    """

    def filter(self, record):
        record.correlation_id = request_id_var.get('')
        return True


def get_correlation_id() -> str:
    """Get the current request's correlation ID."""
    return request_id_var.get('')


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware для добавления уникального Request ID к каждому запросу.

    OBSERVABILITY: Sets correlation ID in context variable for distributed tracing.
    All logs within the request will include this ID.
    """

    async def dispatch(self, request: Request, call_next):
        # Генерация или получение Request ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())[:8]  # Short ID for readability

        # Set in context variable for logging
        token = request_id_var.set(request_id)

        # Сохранение в состоянии запроса для доступа в endpoints
        request.state.request_id = request_id

        try:
            # Обработка запроса
            response = await call_next(request)

            # Добавление Request ID в ответ
            response.headers["X-Request-ID"] = request_id

            return response
        finally:
            # Reset context variable
            request_id_var.reset(token)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования HTTP запросов.

    OBSERVABILITY: Includes correlation ID in all log entries for tracing.
    """

    async def dispatch(self, request: Request, call_next):
        # Начало обработки запроса
        start_time = time.time()
        correlation_id = request_id_var.get('')

        # Логирование входящего запроса (structured format)
        logger.info(
            f"[{correlation_id}] --> {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}",
            extra={
                'correlation_id': correlation_id,
                'method': request.method,
                'path': request.url.path,
                'client': request.client.host if request.client else 'unknown',
                'event': 'request_start'
            }
        )

        # Обработка запроса
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            # Логирование необработанных ошибок
            process_time = time.time() - start_time
            logger.error(
                f"[{correlation_id}] !!! {request.method} {request.url.path} "
                f"error={str(exc)} duration={process_time:.3f}s",
                exc_info=True,
                extra={
                    'correlation_id': correlation_id,
                    'method': request.method,
                    'path': request.url.path,
                    'duration': process_time,
                    'event': 'request_error'
                }
            )
            raise

        # Вычисление времени обработки
        process_time = time.time() - start_time

        # Логирование ответа (structured format)
        log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            log_level,
            f"[{correlation_id}] <-- {request.method} {request.url.path} "
            f"status={response.status_code} duration={process_time:.3f}s",
            extra={
                'correlation_id': correlation_id,
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'duration': process_time,
                'event': 'request_complete'
            }
        )

        # Добавление заголовка с временем обработки
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware для добавления security заголовков

    SECURITY: Усиленная Content Security Policy без unsafe-inline/unsafe-eval
    для защиты от XSS атак
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Добавление security заголовков
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Дополнительные security headers
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Content Security Policy - УСИЛЕННАЯ БЕЗОПАСНОСТЬ
        # Удалены 'unsafe-inline' и 'unsafe-eval' для защиты от XSS
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "  # Убрано unsafe-inline и unsafe-eval
            "style-src 'self'; "   # Убрано unsafe-inline
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )

        return response
