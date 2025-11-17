"""
JSON Helper Functions

DRY: Переиспользуемые функции для работы с JSON
для устранения дублирования кода по всему проекту
"""
import json
from typing import Any, List, Optional


def parse_json_field(
    field: Optional[str],
    default: Any = None
) -> Any:
    """
    Безопасный парсинг JSON поля

    Args:
        field: JSON строка для парсинга
        default: Значение по умолчанию при ошибке

    Returns:
        Распарсенное значение или default

    Example:
        >>> parse_json_field('["item1", "item2"]', [])
        ['item1', 'item2']
        >>> parse_json_field('invalid json', [])
        []
    """
    if not field:
        return default if default is not None else []

    try:
        return json.loads(field)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []


def parse_json_list(
    field: Optional[str],
    default: Optional[List] = None
) -> List:
    """
    Парсинг JSON поля в список

    Args:
        field: JSON строка с массивом
        default: Список по умолчанию

    Returns:
        Распарсенный список или default

    Example:
        >>> parse_json_list('["a", "b", "c"]')
        ['a', 'b', 'c']
    """
    return parse_json_field(field, default if default is not None else [])


def serialize_to_json(
    data: Any,
    default: Optional[str] = None
) -> Optional[str]:
    """
    Безопасная сериализация в JSON

    Args:
        data: Данные для сериализации
        default: Значение при ошибке

    Returns:
        JSON строка или default

    Example:
        >>> serialize_to_json(['item1', 'item2'])
        '["item1", "item2"]'
    """
    if data is None:
        return default

    try:
        return json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError):
        return default


def parse_multiple_json_fields(
    obj: Any,
    fields: List[str],
    default: Any = None
) -> None:
    """
    Парсинг нескольких JSON полей объекта in-place

    Args:
        obj: Объект с JSON полями
        fields: Список имен полей для парсинга
        default: Значение по умолчанию

    Example:
        >>> review = Review(pros='["good"]', cons='["bad"]')
        >>> parse_multiple_json_fields(review, ['pros', 'cons'])
        >>> review.pros
        ['good']
    """
    for field_name in fields:
        if hasattr(obj, field_name):
            field_value = getattr(obj, field_name)
            parsed_value = parse_json_field(field_value, default)
            setattr(obj, field_name, parsed_value)


def batch_parse_json_fields(
    objects: List[Any],
    fields: List[str],
    default: Any = None
) -> List[Any]:
    """
    Парсинг JSON полей для списка объектов

    Args:
        objects: Список объектов
        fields: Список имен полей для парсинга
        default: Значение по умолчанию

    Returns:
        Список объектов с распарсенными полями

    Example:
        >>> reviews = [Review(pros='["a"]'), Review(pros='["b"]')]
        >>> batch_parse_json_fields(reviews, ['pros', 'cons'])
    """
    for obj in objects:
        parse_multiple_json_fields(obj, fields, default)
    return objects
