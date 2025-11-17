"""
Middleware для логирования и мониторинга
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов"""

    async def dispatch(self, request: Request, call_next):
        # Начало обработки запроса
        start_time = time.time()

        # Логирование входящего запроса
        logger.info(
            f"Incoming request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        # Обработка запроса
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            # Логирование необработанных ошибок
            logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
            raise

        # Вычисление времени обработки
        process_time = time.time() - start_time

        # Логирование ответа
        logger.info(
            f"Completed: {request.method} {request.url.path} "
            f"status={response.status_code} duration={process_time:.3f}s"
        )

        # Добавление заголовка с временем обработки
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления security заголовков"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Добавление security заголовков
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:;"
        )

        return response
