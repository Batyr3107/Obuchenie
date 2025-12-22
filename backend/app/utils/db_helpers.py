"""
Database Helper Functions

DRY: Переиспользуемые функции для работы с БД
Устраняет дублирование проверок существования объектов в 10+ местах
"""
from typing import Type, TypeVar, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

T = TypeVar('T')


def get_or_404(
    db: Session,
    model: Type[T],
    obj_id: int,
    error_msg: Optional[str] = None
) -> T:
    """
    Получить объект по ID или вернуть 404

    DRY: Устраняет дублирование кода проверки существования объектов
    Использовалось в 10+ местах с одинаковым паттерном

    Args:
        db: Database session
        model: SQLAlchemy модель
        obj_id: ID объекта
        error_msg: Кастомное сообщение об ошибке

    Returns:
        Найденный объект

    Raises:
        HTTPException: 404 если объект не найден

    Example:
        >>> course = get_or_404(db, Course, course_id)
        >>> user = get_or_404(db, User, user_id, "User not found")
    """
    obj = db.query(model).filter(model.id == obj_id).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg or f"{model.__name__} not found"
        )
    return obj


def get_by_field_or_404(
    db: Session,
    model: Type[T],
    field_name: str,
    field_value: Any,
    error_msg: Optional[str] = None
) -> T:
    """
    Получить объект по полю или вернуть 404

    Args:
        db: Database session
        model: SQLAlchemy модель
        field_name: Имя поля для поиска
        field_value: Значение поля
        error_msg: Кастомное сообщение об ошибке

    Returns:
        Найденный объект

    Raises:
        HTTPException: 404 если объект не найден

    Example:
        >>> user = get_by_field_or_404(db, User, "email", "test@example.com")
    """
    obj = db.query(model).filter(getattr(model, field_name) == field_value).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg or f"{model.__name__} not found"
        )
    return obj


def exists_or_400(
    db: Session,
    model: Type[T],
    field_name: str,
    field_value: Any,
    error_msg: Optional[str] = None
) -> None:
    """
    Проверить, что объект НЕ существует, иначе 400

    Используется для проверки дубликатов (email, название и т.д.)

    Args:
        db: Database session
        model: SQLAlchemy модель
        field_name: Имя поля для проверки
        field_value: Значение поля
        error_msg: Кастомное сообщение об ошибке

    Raises:
        HTTPException: 400 если объект уже существует

    Example:
        >>> exists_or_400(db, User, "email", user_email, "Email already registered")
    """
    obj = db.query(model).filter(getattr(model, field_name) == field_value).first()
    if obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg or f"{model.__name__} already exists"
        )


def safe_commit(db: Session, error_msg: str = "Database operation failed") -> None:
    """
    Безопасный commit с обработкой ошибок

    Args:
        db: Database session
        error_msg: Сообщение об ошибке

    Raises:
        HTTPException: 500 если commit не удался

    Example:
        >>> db.add(new_user)
        >>> safe_commit(db, "Failed to create user")
    """
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{error_msg}: {str(e)}"
        )


def increment_counter(
    db: Session,
    obj: T,
    field_name: str,
    value: int = 1
) -> None:
    """
    Увеличить счетчик у объекта (НЕ атомарно!)

    WARNING: This function has a race condition! Use atomic_increment for
    counters that may be updated concurrently (views, likes, etc.)

    Args:
        db: Database session
        obj: Объект для обновления
        field_name: Имя поля-счетчика
        value: Значение для увеличения (по умолчанию 1)

    Example:
        >>> increment_counter(db, course, "favorites_count")
        >>> increment_counter(db, course, "views_count", 5)
    """
    current_value = getattr(obj, field_name, 0)
    setattr(obj, field_name, current_value + value)


def atomic_increment(
    db: Session,
    model: Type[T],
    obj_id: int,
    field_name: str,
    value: int = 1
) -> None:
    """
    Атомарно увеличить счетчик в БД.

    CONCURRENCY: Использует SQL SET field = field + 1, что предотвращает
    race conditions при одновременных обновлениях.

    Args:
        db: Database session
        model: SQLAlchemy модель
        obj_id: ID объекта
        field_name: Имя поля-счетчика
        value: Значение для увеличения (по умолчанию 1)

    Example:
        >>> atomic_increment(db, Course, course.id, "views_count")
        >>> atomic_increment(db, Review, review.id, "helpful_votes", 1)
    """
    field = getattr(model, field_name)
    db.query(model).filter(model.id == obj_id).update(
        {field_name: field + value},
        synchronize_session=False
    )


def decrement_counter(
    db: Session,
    obj: T,
    field_name: str,
    value: int = 1,
    min_value: int = 0
) -> None:
    """
    Уменьшить счетчик у объекта

    Args:
        db: Database session
        obj: Объект для обновления
        field_name: Имя поля-счетчика
        value: Значение для уменьшения (по умолчанию 1)
        min_value: Минимальное значение (по умолчанию 0)

    Example:
        >>> decrement_counter(db, course, "favorites_count")
    """
    current_value = getattr(obj, field_name, 0)
    new_value = max(min_value, current_value - value)
    setattr(obj, field_name, new_value)
