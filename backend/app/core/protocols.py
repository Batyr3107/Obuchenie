"""
Protocol Definitions (DIP)

Этот модуль содержит Protocol (интерфейсы) для инверсии зависимостей.
Используйте эти протоколы для type hints вместо конкретных реализаций.
"""
from typing import Protocol, Optional, Any, List, runtime_checkable


@runtime_checkable
class ICacheBackend(Protocol):
    """
    Protocol для кэш-бэкенда (DIP).

    Позволяет заменить Redis на любую другую реализацию:
    - Memcached
    - In-memory dict
    - File-based cache
    - Custom implementation

    Example:
        def get_courses(cache: ICacheBackend) -> List[Course]:
            cached = cache.get("courses")
            if cached:
                return cached
            ...
    """

    def get(self, key: str) -> Optional[Any]:
        """Получить значение по ключу"""
        ...

    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Сохранить значение с TTL"""
        ...

    def delete(self, key: str) -> bool:
        """Удалить значение по ключу"""
        ...


@runtime_checkable
class ICacheManager(Protocol):
    """
    Extended cache protocol with pattern operations.
    """

    def get(self, key: str) -> Optional[Any]:
        ...

    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        ...

    def delete(self, key: str) -> bool:
        ...

    def clear_pattern(self, pattern: str) -> int:
        """Удалить ключи по паттерну"""
        ...


@runtime_checkable
class IEmailSender(Protocol):
    """
    Protocol для отправки email (DIP).

    Позволяет заменить FastMail на любую реализацию:
    - SendGrid
    - Mailgun
    - AWS SES
    - Mock для тестов

    Example:
        async def send_notification(sender: IEmailSender):
            await sender.send("user@example.com", "Subject", "<p>Body</p>")
    """

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        is_html: bool = True
    ) -> bool:
        """Отправить email"""
        ...


@runtime_checkable
class IEmailService(Protocol):
    """
    Extended email protocol with template support.
    """

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        is_html: bool = True
    ) -> bool:
        ...

    async def send_template(
        self,
        to: str,
        template_name: str,
        context: dict
    ) -> bool:
        """Отправить email по шаблону"""
        ...


@runtime_checkable
class IRepository(Protocol):
    """
    Generic repository protocol for data access.

    Позволяет абстрагировать доступ к данным:
    - SQLAlchemy
    - MongoDB
    - In-memory для тестов
    """

    def get_by_id(self, id: int) -> Optional[Any]:
        ...

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        ...

    def create(self, data: Any) -> Any:
        ...

    def update(self, id: int, data: Any) -> Optional[Any]:
        ...

    def delete(self, id: int) -> bool:
        ...


@runtime_checkable
class IRedisClient(Protocol):
    """
    Protocol для Redis клиента.
    """

    def get(self, key: str) -> Optional[str]:
        ...

    def set(self, key: str, value: str) -> bool:
        ...

    def setex(self, key: str, ttl: int, value: str) -> bool:
        ...

    def delete(self, *keys: str) -> int:
        ...

    def exists(self, key: str) -> int:
        ...

    def incr(self, key: str) -> int:
        ...

    def expire(self, key: str, seconds: int) -> bool:
        ...

    def scan(self, cursor: int, match: str, count: int) -> tuple:
        ...
