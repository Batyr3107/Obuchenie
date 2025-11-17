"""
Конфигурация логирования
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """
    Настройка логирования для приложения

    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Директория для файлов логов
    """
    # Создание директории для логов
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Настройка формата логов
    log_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Удаление существующих handlers (если есть)
    root_logger.handlers.clear()

    # Console handler - вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

    # File handler - общий лог файл с ротацией
    file_handler = RotatingFileHandler(
        filename=log_path / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)

    # Error file handler - только ошибки
    error_handler = RotatingFileHandler(
        filename=log_path / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    root_logger.addHandler(error_handler)

    # Снижение уровня логирования для сторонних библиотек
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    logging.info(f"Logging configured with level {log_level}")


def get_logger(name: str) -> logging.Logger:
    """
    Получение логгера для модуля

    Args:
        name: Имя модуля (обычно __name__)

    Returns:
        logging.Logger: Настроенный логгер
    """
    return logging.getLogger(name)
