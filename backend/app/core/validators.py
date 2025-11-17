"""
Input validation и sanitization утилиты
"""
import re
from typing import Optional
from fastapi import HTTPException
from urllib.parse import urlparse
import bleach


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Очистка текста от потенциально опасного HTML/JS

    Args:
        text: Текст для очистки
        max_length: Максимальная длина (опционально)

    Returns:
        Очищенный текст
    """
    if not text:
        return ""

    # Удалить HTML теги
    cleaned = bleach.clean(text, tags=[], strip=True)

    # Обрезать если нужно
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]

    # Удалить лишние пробелы
    cleaned = " ".join(cleaned.split())

    return cleaned.strip()


def validate_email(email: str) -> str:
    """
    Валидация email адреса

    Args:
        email: Email для проверки

    Returns:
        Нормализованный email

    Raises:
        HTTPException: Если email невалиден
    """
    email = email.lower().strip()

    # Простая regex валидация
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    # Проверка на опасные символы
    dangerous_chars = ['<', '>', '"', "'", ';', '\\']
    if any(char in email for char in dangerous_chars):
        raise HTTPException(status_code=400, detail="Email contains invalid characters")

    return email


def validate_url(url: str) -> str:
    """
    Валидация URL

    Args:
        url: URL для проверки

    Returns:
        Нормализованный URL

    Raises:
        HTTPException: Если URL невалиден
    """
    url = url.strip()

    try:
        result = urlparse(url)

        # Проверить схему
        if result.scheme not in ['http', 'https']:
            raise HTTPException(
                status_code=400,
                detail="URL must start with http:// or https://"
            )

        # Проверить наличие домена
        if not result.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format")

        return url

    except HTTPException:
        # Пробрасываем HTTPException дальше без изменений
        raise
    except (ValueError, AttributeError) as e:
        # Ошибки парсинга URL
        raise HTTPException(status_code=400, detail=f"Invalid URL format: {str(e)}")


def validate_course_slug(slug: str) -> str:
    """
    Валидация slug для курса

    Args:
        slug: Slug для проверки

    Returns:
        Валидный slug

    Raises:
        HTTPException: Если slug невалиден
    """
    # Slug должен содержать только буквы, цифры, дефисы
    if not re.match(r'^[a-z0-9-]+$', slug):
        raise HTTPException(
            status_code=400,
            detail="Slug can only contain lowercase letters, numbers, and hyphens"
        )

    if len(slug) < 3 or len(slug) > 100:
        raise HTTPException(
            status_code=400,
            detail="Slug must be between 3 and 100 characters"
        )

    return slug


def validate_review_text(text: str) -> str:
    """
    Валидация текста отзыва

    Args:
        text: Текст отзыва

    Returns:
        Очищенный текст

    Raises:
        HTTPException: Если текст невалиден
    """
    text = sanitize_text(text, max_length=5000)

    # Минимальная длина
    if len(text) < 100:
        raise HTTPException(
            status_code=400,
            detail="Review text must be at least 100 characters"
        )

    # Проверка на спам (простая проверка)
    spam_patterns = [
        r'http[s]?://',  # Ссылки
        r'www\.',
        r'@',  # Email
    ]

    for pattern in spam_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise HTTPException(
                status_code=400,
                detail="Review text cannot contain links or email addresses"
            )

    return text


def validate_rating(rating: float, min_val: float = 1.0, max_val: float = 5.0) -> float:
    """
    Валидация рейтинга

    Args:
        rating: Рейтинг для проверки
        min_val: Минимальное значение
        max_val: Максимальное значение

    Returns:
        Валидный рейтинг

    Raises:
        HTTPException: Если рейтинг невалиден
    """
    if not isinstance(rating, (int, float)):
        raise HTTPException(status_code=400, detail="Rating must be a number")

    if rating < min_val or rating > max_val:
        raise HTTPException(
            status_code=400,
            detail=f"Rating must be between {min_val} and {max_val}"
        )

    return round(float(rating), 1)


def detect_sql_injection(text: str) -> bool:
    """
    Простое определение попыток SQL injection

    Args:
        text: Текст для проверки

    Returns:
        True если обнаружена попытка SQL injection
    """
    sql_patterns = [
        r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b.*=.*\bOR\b)",
        r"('.*OR.*'=')",
    ]

    for pattern in sql_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def validate_search_query(query: str) -> str:
    """
    Валидация поискового запроса

    Args:
        query: Поисковый запрос

    Returns:
        Безопасный запрос

    Raises:
        HTTPException: Если запрос опасен
    """
    query = sanitize_text(query, max_length=200)

    if len(query) < 2:
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 2 characters"
        )

    # Проверка на SQL injection
    if detect_sql_injection(query):
        raise HTTPException(
            status_code=400,
            detail="Invalid search query"
        )

    return query
