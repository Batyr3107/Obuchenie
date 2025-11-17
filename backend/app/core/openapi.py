"""
OpenAPI/Swagger конфигурация и улучшения документации
"""
from typing import Dict, Any


# Теги для группировки endpoints
tags_metadata = [
    {
        "name": "Root",
        "description": "Корневые endpoints приложения"
    },
    {
        "name": "Health",
        "description": "Health check endpoints для мониторинга состояния приложения"
    },
    {
        "name": "auth",
        "description": "**Аутентификация и авторизация**. Регистрация, вход, получение токенов.",
    },
    {
        "name": "courses",
        "description": "**Управление курсами**. CRUD операции для образовательных курсов.",
    },
    {
        "name": "reviews",
        "description": "**Отзывы и рейтинги**. Создание, редактирование и модерация отзывов на курсы.",
    },
    {
        "name": "categories",
        "description": "**Категории курсов**. Организация курсов по тематикам.",
    },
    {
        "name": "admin",
        "description": "**Административная панель**. Модерация, управление пользователями и контентом. Требует права администратора.",
    },
    {
        "name": "favorites",
        "description": "**Избранное**. Управление списком избранных курсов пользователя.",
    },
    {
        "name": "reports",
        "description": "**Жалобы**. Система репортов на некорректные отзывы.",
    },
    {
        "name": "compare",
        "description": "**Сравнение курсов**. Сравнительный анализ нескольких курсов.",
    },
    {
        "name": "search",
        "description": "**Поиск**. Поиск курсов с автодополнением и фильтрацией.",
    },
]


# Описание API
description = """
# CourseRate API 🎓

**CourseRate** - платформа для объективной оценки и выбора образовательных курсов.

## Основные возможности

### 📚 Для пользователей
* Поиск и фильтрация курсов по категориям
* Детальная система рейтингов (5 критериев оценки)
* Написание и чтение отзывов
* Сравнение курсов
* Избранные курсы

### 🛡️ Для администраторов
* Модерация курсов и отзывов
* Управление пользователями
* Обработка жалоб
* Статистика платформы

### 💎 Премиум возможности
* Premium размещение курсов
* Расширенная аналитика

## Аутентификация

API использует **JWT Bearer токены**. Получите токен через `/api/v1/auth/login`
и используйте его в заголовке:

```
Authorization: Bearer <your_token>
```

## Ограничения запросов (Rate Limiting)

* **Регистрация**: 5 запросов в час
* **Вход**: 10 запросов в минуту
* **Общий лимит**: 200 запросов в минуту

## Стандартный формат ответов

### Успешный ответ:
```json
{
  "success": true,
  "data": {...},
  "message": "optional message"
}
```

### Ответ с ошибкой:
```json
{
  "success": false,
  "error": "ErrorType",
  "message": "Error description",
  "details": {...}
}
```

### Пагинированный ответ:
```json
{
  "success": true,
  "data": [...],
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## Система рейтингов

Каждый отзыв оценивает курс по **5 критериям** (от 1 до 5 звезд):

1. **Качество контента** - полнота и актуальность материала
2. **Преподаватели** - квалификация и манера подачи
3. **Поддержка** - качество обратной связи
4. **Цена/Качество** - соотношение стоимости и ценности
5. **Практика** - применимость знаний на практике

**Общий рейтинг** = среднее арифметическое всех критериев

## Антиспам защита

* Лимит отзывов: **5 в день**
* Минимальный возраст аккаунта: **3 дня**
* Один отзыв на курс от пользователя
* Модерация всех отзывов

## Технологии

* **Backend**: FastAPI 0.104+
* **Database**: PostgreSQL
* **Cache**: Redis
* **Auth**: JWT
* **Documentation**: OpenAPI 3.0

## Полезные ссылки

* [Документация ReDoc](/redoc)
* [Swagger UI](/docs)
* [Health Check](/health)
* [GitHub Repository](https://github.com/yourusername/courserate)

---

**Версия API**: 1.0.0
**Лицензия**: MIT
"""


# Примеры ответов для повторного использования
response_examples: Dict[str, Dict[str, Any]] = {
    "success": {
        "description": "Успешная операция",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "message": "Operation completed successfully"
                }
            }
        }
    },
    "unauthorized": {
        "description": "Не авторизован",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Authentication required"
                }
            }
        }
    },
    "forbidden": {
        "description": "Доступ запрещен",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": "Forbidden",
                    "message": "You don't have permission to access this resource"
                }
            }
        }
    },
    "not_found": {
        "description": "Ресурс не найден",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": "NotFound",
                    "message": "Resource not found"
                }
            }
        }
    },
    "validation_error": {
        "description": "Ошибка валидации",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": "ValidationError",
                    "message": "Invalid input data",
                    "details": [
                        {
                            "field": "email",
                            "message": "Invalid email format",
                            "type": "value_error.email"
                        }
                    ]
                }
            }
        }
    },
    "rate_limit": {
        "description": "Превышен лимит запросов",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": "RateLimitExceeded",
                    "message": "Rate limit exceeded. Try again later."
                }
            }
        }
    }
}


def custom_openapi_schema():
    """
    Кастомная схема OpenAPI с дополнительной информацией

    Использование в main.py:

    from app.core.openapi import custom_openapi_schema

    app.openapi_schema = custom_openapi_schema()
    """
    return {
        "openapi": "3.0.2",
        "info": {
            "title": "CourseRate API",
            "version": "1.0.0",
            "description": description,
            "contact": {
                "name": "API Support",
                "email": "support@courserate.com",
                "url": "https://courserate.com/support"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "tags": tags_metadata
    }
