"""
Утилиты для санитизации пользовательского ввода
Защита от XSS атак и вредоносного контента
"""
import bleach
from typing import Optional, List
import re


# Разрешённые HTML теги для богатого текста (например, в отзывах)
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre'
]

# Разрешённые атрибуты для тегов
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'img': ['src', 'alt', 'title'],
}

# Разрешённые протоколы для ссылок
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def sanitize_html(
    text: Optional[str],
    allowed_tags: List[str] = None,
    strip: bool = False
) -> str:
    """
    Санитизация HTML контента с сохранением разрешённых тегов

    Args:
        text: Исходный текст
        allowed_tags: Список разрешённых тегов (по умолчанию ALLOWED_TAGS)
        strip: Если True, удаляет теги полностью, иначе экранирует

    Returns:
        Санитизированный текст
    """
    if text is None:
        return ""

    if allowed_tags is None:
        allowed_tags = ALLOWED_TAGS

    # Очистка с помощью bleach
    cleaned = bleach.clean(
        text,
        tags=allowed_tags,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=strip
    )

    return cleaned


def sanitize_text(text: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Полная санитизация текста - удаление всех HTML тегов

    Args:
        text: Исходный текст
        max_length: Максимальная длина (опционально)

    Returns:
        Санитизированный обычный текст
    """
    if text is None:
        return ""

    # Удаление всех HTML тегов
    cleaned = bleach.clean(text, tags=[], strip=True)

    # Удаление лишних пробелов
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Ограничение длины
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]

    return cleaned


def sanitize_url(url: Optional[str]) -> Optional[str]:
    """
    Санитизация URL

    Args:
        url: URL для проверки

    Returns:
        Санитизированный URL или None если невалидный
    """
    if not url:
        return None

    # Удаление пробелов
    url = url.strip()

    # Проверка протокола
    if not url.startswith(('http://', 'https://')):
        # Если протокол не указан, добавляем https://
        url = f"https://{url}"

    # Проверка на вредоносные паттерны
    dangerous_patterns = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:',
    ]

    url_lower = url.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, url_lower):
            return None

    # Базовая валидация URL
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    if url_pattern.match(url):
        return url

    return None


def sanitize_email(email: Optional[str]) -> Optional[str]:
    """
    Санитизация email адреса

    Args:
        email: Email для проверки

    Returns:
        Санитизированный email или None
    """
    if not email:
        return None

    # Удаление пробелов и приведение к lowercase
    email = email.strip().lower()

    # Простая валидация email
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    if email_pattern.match(email):
        return email

    return None


def sanitize_search_query(query: Optional[str]) -> str:
    """
    Санитизация поискового запроса

    Args:
        query: Поисковый запрос

    Returns:
        Санитизированный запрос
    """
    if not query:
        return ""

    # Удаление HTML тегов
    cleaned = bleach.clean(query, tags=[], strip=True)

    # Удаление специальных символов SQL
    cleaned = re.sub(r'[;\'\"\\]', '', cleaned)

    # Ограничение длины
    cleaned = cleaned[:200]

    # Удаление лишних пробелов
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned


def sanitize_slug(text: str) -> str:
    """
    Создание безопасного slug из текста

    Args:
        text: Исходный текст

    Returns:
        Безопасный slug
    """
    # Приведение к нижнему регистру
    slug = text.lower()

    # Транслитерация русских букв
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }

    for cyrillic, latin in translit_map.items():
        slug = slug.replace(cyrillic, latin)

    # Удаление всех символов кроме букв, цифр и дефисов
    slug = re.sub(r'[^a-z0-9-]+', '-', slug)

    # Удаление повторяющихся дефисов
    slug = re.sub(r'-+', '-', slug)

    # Удаление дефисов в начале и конце
    slug = slug.strip('-')

    # Ограничение длины
    slug = slug[:100]

    return slug


def sanitize_json_string(text: Optional[str]) -> str:
    """
    Санитизация строки для безопасного использования в JSON

    Args:
        text: Исходный текст

    Returns:
        Безопасная строка для JSON
    """
    if not text:
        return ""

    # Удаление управляющих символов
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    # Экранирование специальных символов JSON
    cleaned = cleaned.replace('\\', '\\\\')
    cleaned = cleaned.replace('"', '\\"')
    cleaned = cleaned.replace('\n', '\\n')
    cleaned = cleaned.replace('\r', '\\r')
    cleaned = cleaned.replace('\t', '\\t')

    return cleaned
