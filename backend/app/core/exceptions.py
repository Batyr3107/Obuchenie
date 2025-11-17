"""
Глобальная обработка исключений
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработка ошибок валидации Pydantic"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(f"Validation error on {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation Error",
            "details": errors
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Обработка ошибок базы данных"""
    logger.error(f"Database error on {request.url.path}: {str(exc)}")

    # Не показываем детали БД ошибок пользователю в production
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Database Error",
            "message": "An error occurred while processing your request"
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Обработка ошибок целостности БД (duplicate keys, foreign keys)"""
    logger.error(f"Integrity error on {request.url.path}: {str(exc)}")

    error_message = "A database constraint was violated"

    # Попытка определить тип ошибки
    error_str = str(exc.orig).lower()
    if "unique" in error_str or "duplicate" in error_str:
        error_message = "This record already exists"
    elif "foreign key" in error_str:
        error_message = "Related record not found"

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "error": "Integrity Error",
            "message": error_message
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Обработка всех остальных исключений"""
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


class AppException(Exception):
    """Базовое исключение приложения"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def app_exception_handler(request: Request, exc: AppException):
    """Обработка пользовательских исключений приложения"""
    logger.warning(f"App exception on {request.url.path}: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "Application Error",
            "message": exc.message
        }
    )
