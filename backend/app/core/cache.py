"""
Redis кэширование

SECURITY NOTE: Используется JSON сериализация вместо pickle для
предотвращения уязвимостей arbitrary code execution при десериализации.
"""
import json
import enum
from typing import Optional, Any, Callable
from functools import wraps
import hashlib
import logging
from datetime import datetime, date
from decimal import Decimal

try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Менеджер кэширования с поддержкой Redis"""

    def __init__(self):
        self.redis_client: Optional[Redis] = None
        self.enabled = False

        if REDIS_AVAILABLE and hasattr(settings, 'REDIS_HOST'):
            try:
                self.redis_client = redis.Redis(
                    host=getattr(settings, 'REDIS_HOST', 'localhost'),
                    port=getattr(settings, 'REDIS_PORT', 6379),
                    db=getattr(settings, 'REDIS_DB', 0),
                    password=getattr(settings, 'REDIS_PASSWORD', None),
                    decode_responses=False,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Проверка подключения
                self.redis_client.ping()
                self.enabled = True
                logger.info("Redis cache enabled successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Cache disabled.")
                self.redis_client = None
                self.enabled = False
        else:
            logger.info("Redis not configured. Cache disabled.")

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Генерация ключа кэша"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"cache:{prefix}:{key_hash}"

    def _json_serializer(self, obj: Any) -> Any:
        """
        Кастомный JSON сериализатор для сложных объектов

        PERFORMANCE: Handles SQLAlchemy objects by converting to dict
        Поддерживает datetime, date, Decimal, set, SQLAlchemy models, Enum
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        # Handle Python Enum objects (including SQLAlchemy enums)
        if isinstance(obj, enum.Enum):
            return obj.value
        # Handle SQLAlchemy model objects
        if hasattr(obj, '__table__'):
            result = {}
            for c in obj.__table__.columns:
                value = getattr(obj, c.name)
                # Recursively serialize column values
                if isinstance(value, (datetime, date)):
                    result[c.name] = value.isoformat()
                elif isinstance(value, enum.Enum):
                    result[c.name] = value.value
                elif isinstance(value, Decimal):
                    result[c.name] = float(value)
                else:
                    result[c.name] = value
            return result
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def get(self, key: str) -> Optional[Any]:
        """
        Получение значения из кэша

        SECURITY: Использует JSON десериализацию вместо pickle
        для предотвращения arbitrary code execution
        """
        if not self.enabled or not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                # Безопасная десериализация через JSON
                return json.loads(value.decode('utf-8'))
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        expire: int = 3600
    ) -> bool:
        """
        Сохранение значения в кэш

        Args:
            key: Ключ кэша
            value: Значение для сохранения
            expire: Время жизни в секундах (по умолчанию 1 час)

        Returns:
            bool: Успешность операции

        SECURITY: Использует JSON сериализацию вместо pickle
        для предотвращения arbitrary code execution
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            # Безопасная сериализация через JSON
            serialized = json.dumps(value, default=self._json_serializer)
            self.redis_client.setex(key, expire, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Удаление значения из кэша"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Удаление ключей по шаблону

        PERFORMANCE: Uses SCAN instead of KEYS to avoid blocking Redis.
        KEYS is O(N) and blocks the entire Redis instance.
        SCAN iterates incrementally without blocking.

        Args:
            pattern: Шаблон ключа (например, "user:*")

        Returns:
            int: Количество удаленных ключей
        """
        if not self.enabled or not self.redis_client:
            return 0

        try:
            deleted = 0
            cursor = 0
            # PERFORMANCE: Use SCAN instead of KEYS to avoid blocking Redis
            while True:
                cursor, keys = self.redis_client.scan(
                    cursor=cursor,
                    match=f"cache:{pattern}",
                    count=100  # Process 100 keys per iteration
                )
                if keys:
                    deleted += self.redis_client.delete(*keys)
                if cursor == 0:
                    break
            return deleted
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0

    def clear_all(self) -> bool:
        """Очистка всего кэша"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Cache clear all error: {e}")
            return False


# Глобальный экземпляр менеджера кэша
cache_manager = CacheManager()


def cached(
    prefix: str = "default",
    expire: int = 3600,
    key_builder: Optional[Callable] = None
):
    """
    Декоратор для кэширования результатов функции

    Args:
        prefix: Префикс ключа кэша
        expire: Время жизни кэша в секундах
        key_builder: Пользовательская функция для генерации ключа

    Example:
        @cached(prefix="courses", expire=1800)
        def get_courses():
            return db.query(Course).all()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Если кэш отключен, вызываем функцию напрямую
            if not cache_manager.enabled:
                return func(*args, **kwargs)

            # Генерация ключа
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache_manager._generate_key(prefix, *args, **kwargs)

            # Попытка получить из кэша
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT for key: {cache_key}")
                return cached_value

            # Вызов функции и сохранение результата
            logger.debug(f"Cache MISS for key: {cache_key}")
            result = func(*args, **kwargs)

            # Сохранение в кэш
            cache_manager.set(cache_key, result, expire)

            return result

        # Добавляем метод для инвалидации кэша
        wrapper.invalidate = lambda *args, **kwargs: cache_manager.delete(
            key_builder(*args, **kwargs) if key_builder
            else cache_manager._generate_key(prefix, *args, **kwargs)
        )

        return wrapper

    return decorator


def invalidate_cache(pattern: str):
    """
    Инвалидация кэша по шаблону

    Args:
        pattern: Шаблон для поиска ключей

    Example:
        invalidate_cache("courses:*")
    """
    return cache_manager.clear_pattern(pattern)


# Примеры использования:
"""
# В эндпоинте:
@router.get("/courses")
@cached(prefix="courses_list", expire=1800)
async def get_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

# Инвалидация после создания курса:
@router.post("/courses")
async def create_course(course_data: CourseCreate, db: Session = Depends(get_db)):
    course = Course(**course_data.dict())
    db.add(course)
    db.commit()

    # Инвалидация кэша списка курсов
    invalidate_cache("courses_list:*")

    return course
"""
