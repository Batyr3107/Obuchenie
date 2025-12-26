"""
Стандартизированные модели ответов API
"""
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


DataT = TypeVar('DataT')


class ResponseBase(BaseModel):
    """Базовая модель ответа"""
    success: bool = Field(..., description="Статус выполнения запроса")
    message: Optional[str] = Field(None, description="Сообщение для пользователя")


class SuccessResponse(ResponseBase, Generic[DataT]):
    """Успешный ответ с данными"""
    success: bool = Field(default=True, description="Всегда True для успешных ответов")
    data: DataT = Field(..., description="Данные ответа")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "message": "Operation completed successfully",
            "data": {"id": 1, "name": "Example"}
        }
    })


class ErrorResponse(ResponseBase):
    """Ответ с ошибкой"""
    success: bool = Field(default=False, description="Всегда False для ошибок")
    error: str = Field(..., description="Тип ошибки")
    details: Optional[Any] = Field(None, description="Детали ошибки")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": False,
            "message": "Validation failed",
            "error": "ValidationError",
            "details": {"field": "email", "message": "Invalid email format"}
        }
    })


class PaginationMeta(BaseModel):
    """Метаданные пагинации"""
    total: int = Field(..., description="Общее количество элементов")
    page: int = Field(..., description="Текущая страница")
    per_page: int = Field(..., description="Элементов на странице")
    total_pages: int = Field(..., description="Всего страниц")
    has_next: bool = Field(..., description="Есть ли следующая страница")
    has_prev: bool = Field(..., description="Есть ли предыдущая страница")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total": 100,
            "page": 1,
            "per_page": 20,
            "total_pages": 5,
            "has_next": True,
            "has_prev": False
        }
    })


class PaginatedResponse(SuccessResponse[List[DataT]]):
    """Ответ с пагинированными данными"""
    meta: PaginationMeta = Field(..., description="Метаданные пагинации")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "message": "Data retrieved successfully",
            "data": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
            "meta": {
                "total": 100,
                "page": 1,
                "per_page": 20,
                "total_pages": 5,
                "has_next": True,
                "has_prev": False
            }
        }
    })


class MessageResponse(ResponseBase):
    """Простой ответ с сообщением (без данных)"""
    success: bool = Field(default=True, description="Статус операции")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "message": "Operation completed successfully"
        }
    })


# Хелпер функции для создания ответов
def success_response(
    data: Any,
    message: Optional[str] = None
) -> dict:
    """
    Создает успешный ответ

    Args:
        data: Данные для ответа
        message: Опциональное сообщение

    Returns:
        dict: Стандартизированный ответ
    """
    response = {
        "success": True,
        "data": data
    }
    if message:
        response["message"] = message
    return response


def error_response(
    error: str,
    message: str,
    details: Optional[Any] = None
) -> dict:
    """
    Создает ответ с ошибкой

    Args:
        error: Тип ошибки
        message: Сообщение об ошибке
        details: Опциональные детали

    Returns:
        dict: Стандартизированный ответ с ошибкой
    """
    response = {
        "success": False,
        "error": error,
        "message": message
    }
    if details:
        response["details"] = details
    return response


def paginated_response(
    data: List[Any],
    total: int,
    page: int,
    per_page: int,
    message: Optional[str] = None
) -> dict:
    """
    Создает пагинированный ответ

    Args:
        data: Список данных
        total: Общее количество элементов
        page: Текущая страница
        per_page: Элементов на странице
        message: Опциональное сообщение

    Returns:
        dict: Стандартизированный пагинированный ответ
    """
    import math

    total_pages = math.ceil(total / per_page) if per_page > 0 else 0

    response = {
        "success": True,
        "data": data,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    if message:
        response["message"] = message
    return response


def message_response(message: str, success: bool = True) -> dict:
    """
    Создает простой ответ с сообщением

    Args:
        message: Сообщение
        success: Статус успеха

    Returns:
        dict: Ответ с сообщением
    """
    return {
        "success": success,
        "message": message
    }
