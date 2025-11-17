# Advanced Features Documentation

Документация по расширенным функциям и улучшениям проекта CourseRate.

---

## 📋 Содержание

1. [Alembic Database Migrations](#alembic-database-migrations)
2. [Standardized API Responses](#standardized-api-responses)
3. [Redis Caching Layer](#redis-caching-layer)
4. [Enhanced OpenAPI Documentation](#enhanced-openapi-documentation)
5. [Soft Delete Pattern](#soft-delete-pattern)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Pre-commit Hooks](#pre-commit-hooks)

---

## 1. Alembic Database Migrations

### Настройка

Alembic уже настроен и готов к использованию. Конфигурация находится в:
- `backend/alembic.ini` - основная конфигурация
- `backend/alembic/env.py` - настройка окружения
- `backend/alembic/versions/` - директория для миграций

### Использование

```bash
cd backend

# Создание новой миграции
alembic revision --autogenerate -m "Описание изменений"

# Просмотр текущей версии БД
alembic current

# Просмотр истории миграций
alembic history

# Применение миграций
alembic upgrade head

# Откат последней миграции
alembic downgrade -1

# Откат к конкретной версии
alembic downgrade <revision_id>
```

### Автогенерация миграций

Alembic автоматически обнаружит изменения в моделях:

```python
# Изменили модель
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    # Добавили новое поле
    phone = Column(String(20), nullable=True)
```

```bash
# Создаем миграцию
alembic revision --autogenerate -m "Add phone field to User"

# Применяем
alembic upgrade head
```

### Best Practices

1. **Всегда проверяйте** сгенерированные миграции перед применением
2. **Не редактируйте** уже примененные миграции
3. **Делайте бэкап** БД перед применением миграций в production
4. **Пишите тесты** для критичных миграций

---

## 2. Standardized API Responses

### Структура ответов

Все API endpoints используют стандартизированный формат ответов:

#### Успешный ответ:
```json
{
  "success": true,
  "data": { "id": 1, "name": "Course Name" },
  "message": "Optional success message"
}
```

#### Ответ с ошибкой:
```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Invalid input data",
  "details": {
    "field": "email",
    "message": "Invalid email format"
  }
}
```

#### Пагинированный ответ:
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

### Использование в коде

```python
from app.schemas.response import (
    success_response,
    error_response,
    paginated_response,
    message_response
)

# В endpoint'е:
@router.get("/courses")
async def get_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    return success_response(
        data=[course.to_dict() for course in courses],
        message="Courses retrieved successfully"
    )

# Пагинация:
@router.get("/courses/paginated")
async def get_courses_paginated(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    total = db.query(Course).count()
    courses = db.query(Course).offset((page-1)*per_page).limit(per_page).all()

    return paginated_response(
        data=[course.to_dict() for course in courses],
        total=total,
        page=page,
        per_page=per_page
    )
```

---

## 3. Redis Caching Layer

### Настройка

1. Убедитесь что Redis запущен:
```bash
docker-compose up -d redis
```

2. Настройте переменные окружения в `.env`:
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
ENABLE_CACHE=true
```

### Использование декоратора @cached

```python
from app.core.cache import cached, invalidate_cache

# Кэширование на 30 минут
@router.get("/courses")
@cached(prefix="courses_list", expire=1800)
async def get_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

# Инвалидация кэша при создании
@router.post("/courses")
async def create_course(course_data: CourseCreate, db: Session = Depends(get_db)):
    course = Course(**course_data.dict())
    db.add(course)
    db.commit()

    # Удаляем кэш списка курсов
    invalidate_cache("courses_list:*")

    return success_response(data=course.to_dict())
```

### Прямое использование cache_manager

```python
from app.core.cache import cache_manager

# Сохранение
cache_manager.set("my_key", {"data": "value"}, expire=3600)

# Получение
value = cache_manager.get("my_key")

# Удаление
cache_manager.delete("my_key")

# Удаление по шаблону
cache_manager.clear_pattern("courses:*")
```

### Стратегии кэширования

**Что кэшировать:**
- ✅ Списки курсов (часто читаются, редко меняются)
- ✅ Детали курса
- ✅ Категории
- ✅ Рейтинги и статистика
- ✅ Результаты поиска

**Что НЕ кэшировать:**
- ❌ Данные пользователя (часто меняются)
- ❌ Токены аутентификации
- ❌ Real-time данные

**Время жизни:**
- Статичные данные (категории): 24 часа
- Списки курсов: 30 минут - 1 час
- Детали курса: 15-30 минут
- Результаты поиска: 5-10 минут

---

## 4. Enhanced OpenAPI Documentation

### Особенности

- 📚 Детальное описание всех endpoints
- 🏷️ Группировка по тегам
- 📝 Примеры запросов и ответов
- 🔒 Схемы аутентификации
- ⚡ Интерактивная Swagger UI

### Доступ к документации

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json

### Кастомизация

Теги и описания находятся в `backend/app/core/openapi.py`:

```python
tags_metadata = [
    {
        "name": "courses",
        "description": "Управление курсами. CRUD операции.",
    },
    # ...
]
```

### Добавление примеров в endpoint

```python
from app.core.openapi import response_examples

@router.post("/login", responses={
    200: response_examples["success"],
    401: response_examples["unauthorized"],
    429: response_examples["rate_limit"]
})
async def login(...):
    ...
```

---

## 5. Soft Delete Pattern

### Что это?

Soft Delete - это паттерн "мягкого удаления", при котором записи не удаляются физически из БД, а помечаются как удаленные.

### Преимущества

- ✅ Возможность восстановления данных
- ✅ Сохранение истории
- ✅ Соответствие GDPR (audit trail)
- ✅ Защита от случайного удаления

### Использование

```python
from app.models.mixins import SoftDeleteMixin, TimestampMixin

class Course(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    # Автоматически добавятся:
    # - deleted_at
    # - is_deleted
    # - created_at
    # - updated_at
```

```python
# Мягкое удаление
course = db.query(Course).first()
course.soft_delete()
db.commit()

# Восстановление
course.restore()
db.commit()

# Запросы только активных
active_courses = db.query(Course).filter(Course.is_deleted == False).all()

# Или с использованием helper
active_courses = Course.active(db.query(Course)).all()

# Удаленные записи
deleted_courses = Course.deleted(db.query(Course)).all()

# Все записи (включая удаленные)
all_courses = Course.with_deleted(db.query(Course)).all()
```

### Full Audit Mixin

Для важных данных используйте `FullAuditMixin`:

```python
from app.models.mixins import FullAuditMixin

class ImportantData(Base, FullAuditMixin):
    __tablename__ = "important_data"
    # Автоматически добавятся:
    # - created_at, updated_at, deleted_at
    # - created_by_id, updated_by_id, deleted_by_id
    # - is_deleted
```

---

## 6. CI/CD Pipeline

### GitHub Actions Workflow

Pipeline автоматически запускается при:
- Push в `main` или `develop`
- Pull Request в `main` или `develop`

### Этапы

1. **Backend Tests**
   - Запуск PostgreSQL и Redis в Docker
   - Установка зависимостей
   - Линтинг (flake8)
   - Type checking (mypy)
   - Запуск тестов с coverage

2. **Frontend Tests**
   - Установка Node.js зависимостей
   - ESLint проверка
   - Запуск тестов
   - Build приложения

3. **Security Checks**
   - Safety check (Python уязвимости)
   - Bandit (security linting)
   - npm audit (JS уязвимости)

4. **Docker Build**
   - Build production образов
   - Проверка успешности сборки

5. **Deploy** (только для main)
   - Автоматический деплой в production

### Локальный запуск тестов

```bash
# Backend
cd backend
pytest --cov=app --cov-report=html

# Frontend
cd frontend
npm test
npm run build
```

### Coverage Report

После запуска тестов coverage доступен в:
- Terminal output
- `backend/htmlcov/index.html`

---

## 7. Pre-commit Hooks

### Установка

```bash
# Установка pre-commit
pip install pre-commit

# Установка hooks в репозитории
pre-commit install

# Запуск вручную для всех файлов
pre-commit run --all-files
```

### Что проверяется?

#### Python (Backend):
- ✅ **Black** - форматирование кода
- ✅ **isort** - сортировка импортов
- ✅ **flake8** - линтинг
- ✅ **mypy** - type checking
- ✅ **bandit** - security проверки

#### JavaScript (Frontend):
- ✅ **ESLint** - линтинг
- ✅ **Prettier** - форматирование

#### Общее:
- ✅ Trailing whitespace
- ✅ End of file fixer
- ✅ Large files check
- ✅ Private key detection
- ✅ YAML/JSON validation

### Обход hooks (не рекомендуется)

```bash
git commit --no-verify -m "Message"
```

### Обновление hooks

```bash
pre-commit autoupdate
```

---

## 🚀 Quick Start Guide

### 1. Первоначальная настройка

```bash
# 1. Клонирование репозитория
git clone <repo_url>
cd Obuchenie

# 2. Установка pre-commit hooks
pip install pre-commit
pre-commit install

# 3. Копирование .env файлов
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 4. Редактирование .env файлов
nano backend/.env  # настроить DATABASE_URL, REDIS_HOST, etc.
```

### 2. Запуск с Docker

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Миграции БД

```bash
cd backend

# Создание и применение миграций
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. Запуск тестов

```bash
# Backend
cd backend
pytest --cov=app

# Frontend
cd frontend
npm test
```

---

## 📚 Дополнительные ресурсы

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Redis Caching Best Practices](https://redis.io/docs/manual/patterns/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Pre-commit Framework](https://pre-commit.com/)

---

**Дата обновления**: 2025-11-17
**Версия**: 1.0
