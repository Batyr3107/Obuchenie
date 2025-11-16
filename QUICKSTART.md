# CourseRate - Быстрый старт

Инструкция по быстрому запуску проекта.

## Предварительные требования

- Docker и Docker Compose (рекомендуется)
- ИЛИ:
  - Python 3.11+
  - PostgreSQL 15+
  - Node.js 18+
  - npm или yarn

## Вариант 1: Запуск с Docker (рекомендуется)

### 1. Клонирование и настройка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd Obuchenie

# Скопировать и настроить переменные окружения
cp .env.example .env

# Отредактируйте .env если нужно (можно оставить по умолчанию для локального запуска)
```

### 2. Запуск всех сервисов

```bash
# Запустить все сервисы (PostgreSQL, Redis, Backend)
docker-compose up -d

# Просмотр логов
docker-compose logs -f backend
```

### 3. Инициализация базы данных

```bash
# Войти в контейнер backend
docker-compose exec backend bash

# Выполнить скрипт инициализации
python -m app.db.init_db

# Выйти из контейнера
exit
```

### 4. Запуск Frontend

```bash
cd frontend

# Установка зависимостей
npm install

# Создать .env файл
cp .env.example .env

# Запуск dev сервера
npm run dev
```

### 5. Готово! 🎉

Откройте в браузере:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

**Данные для входа (админ):**
- Email: `admin@courserate.com`
- Password: `changethis123`

⚠️ **Важно**: Смените пароль администратора после первого входа!

---

## Вариант 2: Запуск без Docker

### 1. Настройка PostgreSQL

```bash
# Создание базы данных
createdb courserate

# Или через psql
psql -U postgres
CREATE DATABASE courserate;
\q
```

### 2. Backend

```bash
cd backend

# Создание виртуального окружения
python -m venv venv

# Активация
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp ../.env.example ../.env

# Отредактируйте .env файл с вашими настройками БД:
# DATABASE_URL=postgresql://username:password@localhost:5432/courserate

# Инициализация БД
python -m app.db.init_db

# Запуск сервера
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend

```bash
# В новом терминале
cd frontend

# Установка зависимостей
npm install

# Создание .env файла
cp .env.example .env

# Запуск dev сервера
npm run dev
```

### 4. Готово! 🎉

Откройте в браузере:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Тестирование функционала

### 1. Регистрация пользователя

1. Откройте http://localhost:3000/register
2. Зарегистрируйте нового пользователя
3. Войдите в систему

### 2. Добавление курса

1. Перейдите на "Добавить курс"
2. Заполните форму
3. Отправьте на модерацию

### 3. Модерация курса (админ)

1. Войдите как администратор
2. API для одобрения: `POST /api/v1/courses/{id}/approve`
3. Используйте Swagger UI: http://localhost:8000/docs

### 4. Добавление отзыва

1. Откройте страницу курса
2. Нажмите "Написать отзыв"
3. Заполните оценки и текст отзыва
4. Отправьте

---

## Полезные команды

### Docker

```bash
# Остановить все сервисы
docker-compose down

# Перезапустить
docker-compose restart

# Просмотр логов
docker-compose logs -f

# Очистка (удалить все данные)
docker-compose down -v

# Войти в контейнер БД
docker-compose exec db psql -U courseuser -d courserate
```

### Makefile

```bash
# Если установлен make
make run      # Запустить
make stop     # Остановить
make logs     # Логи
make clean    # Очистить
make db-shell # Shell БД
```

---

## Решение проблем

### Backend не запускается

```bash
# Проверить подключение к БД
docker-compose exec backend python -c "from app.db.base import engine; print(engine.url)"

# Пересоздать таблицы
docker-compose exec backend python -m app.db.init_db
```

### Frontend не подключается к Backend

1. Проверьте `.env` файл в frontend:
   ```
   VITE_API_URL=http://localhost:8000/api/v1
   ```

2. Перезапустите dev сервер:
   ```bash
   npm run dev
   ```

### Ошибки CORS

Убедитесь, что в `.env` указаны правильные CORS origins:
```
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

---

## Следующие шаги

1. Измените пароль администратора
2. Добавьте свои категории через админку
3. Добавьте тестовые курсы
4. Настройте email (опционально)
5. Прочитайте полную документацию в README.md

---

Если возникли проблемы, создайте issue в репозитории!
