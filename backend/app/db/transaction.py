"""
Database transaction utilities
Утилиты для работы с транзакциями БД
"""
from contextlib import contextmanager
from sqlalchemy.orm import Session
from typing import Generator
import logging

logger = logging.getLogger(__name__)


@contextmanager
def transactional_session(db: Session) -> Generator[Session, None, None]:
    """
    Context manager для транзакционной обработки БД

    Автоматически делает commit при успехе и rollback при ошибке

    Usage:
        with transactional_session(db) as session:
            session.add(new_object)
            # При успехе автоматически commit
            # При ошибке автоматически rollback

    Args:
        db: SQLAlchemy Session

    Yields:
        Session: Та же сессия БД
    """
    try:
        yield db
        db.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction rolled back due to error: {str(e)}")
        raise
    finally:
        db.close()


def atomic_operation(db: Session):
    """
    Decorator для атомарных операций с БД

    Usage:
        @atomic_operation
        def create_user_with_profile(db: Session, user_data, profile_data):
            user = User(**user_data)
            db.add(user)
            db.flush()  # Получить user.id

            profile = Profile(**profile_data, user_id=user.id)
            db.add(profile)
            # Автоматически commit если нет ошибок
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                db.commit()
                logger.debug(f"Atomic operation {func.__name__} committed")
                return result
            except Exception as e:
                db.rollback()
                logger.error(f"Atomic operation {func.__name__} rolled back: {str(e)}")
                raise
        return wrapper
    return decorator
