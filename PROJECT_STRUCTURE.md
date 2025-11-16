# Структура проекта CourseRate

```
Obuchenie/
├── backend/                      # Backend API (FastAPI)
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies/     # Зависимости (auth, и т.д.)
│   │   │   │   └── auth.py       # JWT аутентификация
│   │   │   └── endpoints/        # API endpoints
│   │   │       ├── auth.py       # Регистрация, вход
│   │   │       ├── courses.py    # CRUD курсов
│   │   │       ├── reviews.py    # CRUD отзывов
│   │   │       └── categories.py # Категории и подкатегории
│   │   ├── core/                 # Конфигурация
│   │   │   ├── config.py         # Настройки приложения
│   │   │   └── security.py       # Хеширование паролей, JWT
│   │   ├── db/                   # База данных
│   │   │   ├── base.py           # SQLAlchemy setup
│   │   │   └── init_db.py        # Скрипт инициализации
│   │   ├── models/               # SQLAlchemy модели
│   │   │   ├── user.py           # Пользователи
│   │   │   ├── course.py         # Курсы
│   │   │   ├── review.py         # Отзывы
│   │   │   ├── category.py       # Категории
│   │   │   ├── tag.py            # Теги
│   │   │   ├── favorite.py       # Избранное
│   │   │   ├── report.py         # Жалобы
│   │   │   └── premium_placement.py # Премиум размещение
│   │   ├── schemas/              # Pydantic схемы
│   │   │   ├── user.py
│   │   │   ├── course.py
│   │   │   ├── review.py
│   │   │   └── category.py
│   │   └── main.py               # Главный файл приложения
│   ├── requirements.txt          # Python зависимости
│   └── Dockerfile               # Docker образ для backend
│
├── frontend/                     # Frontend (React + Vite)
│   ├── public/                   # Статические файлы
│   ├── src/
│   │   ├── components/           # React компоненты
│   │   │   ├── common/
│   │   │   │   ├── Layout.jsx    # Основной layout
│   │   │   │   ├── Header.jsx    # Шапка сайта
│   │   │   │   └── Footer.jsx    # Подвал
│   │   │   ├── courses/
│   │   │   │   ├── CourseCard.jsx      # Карточка курса
│   │   │   │   └── CourseFilters.jsx   # Фильтры курсов
│   │   │   └── reviews/
│   │   │       ├── ReviewCard.jsx      # Карточка отзыва
│   │   │       └── RatingStars.jsx     # Звездочки рейтинга
│   │   ├── pages/                # Страницы
│   │   │   ├── HomePage.jsx           # Главная страница
│   │   │   ├── CoursesPage.jsx        # Список курсов
│   │   │   ├── CourseDetailPage.jsx   # Детали курса
│   │   │   ├── LoginPage.jsx          # Вход
│   │   │   ├── RegisterPage.jsx       # Регистрация
│   │   │   ├── ProfilePage.jsx        # Профиль
│   │   │   └── AddCoursePage.jsx      # Добавление курса
│   │   ├── services/
│   │   │   └── api.js            # API клиент (axios)
│   │   ├── utils/
│   │   │   └── store.js          # Zustand store (state management)
│   │   ├── styles/
│   │   │   └── index.css         # Tailwind CSS стили
│   │   ├── App.jsx               # Главный компонент
│   │   └── main.jsx              # Entry point
│   ├── package.json              # npm зависимости
│   ├── vite.config.js            # Конфигурация Vite
│   ├── tailwind.config.js        # Конфигурация Tailwind
│   └── index.html                # HTML template
│
├── docs/                         # Документация
├── .env.example                  # Пример переменных окружения
├── .gitignore                    # Git ignore файл
├── docker-compose.yml            # Docker Compose (dev)
├── Makefile                      # Команды для запуска
├── README.md                     # Основная документация
├── QUICKSTART.md                 # Быстрый старт
└── DEPLOYMENT.md                 # Деплой в production
```

## Основные технологии

### Backend
- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM
- **PostgreSQL** - база данных
- **Pydantic** - валидация данных
- **JWT** - аутентификация
- **Redis** - кэширование

### Frontend
- **React 18** - UI библиотека
- **Vite** - сборщик
- **TailwindCSS** - стилизация
- **React Router** - роутинг
- **Zustand** - state management
- **Axios** - HTTP клиент
- **React Hot Toast** - уведомления

### DevOps
- **Docker & Docker Compose**
- **Nginx** - веб-сервер
- **Let's Encrypt** - SSL

## Основные функции

### Реализовано ✅

#### Backend API
- [x] Регистрация и аутентификация (JWT)
- [x] CRUD операции для курсов
- [x] CRUD операции для отзывов
- [x] Система рейтингов (5 критериев)
- [x] Категории и подкатегории
- [x] Фильтрация и поиск курсов
- [x] Модерация курсов (admin)
- [x] Антиспам меры (лимиты, возраст аккаунта)
- [x] Автоматический пересчет рейтингов

#### Frontend
- [x] Главная страница с топ курсами
- [x] Список всех курсов с фильтрами
- [x] Детальная страница курса
- [x] Система отзывов с детальными оценками
- [x] Регистрация и вход
- [x] Профиль пользователя
- [x] Добавление курсов
- [x] Адаптивный дизайн

#### База данных
- [x] 8 таблиц (Users, Courses, Reviews, Categories, etc.)
- [x] Связи между таблицами
- [x] Индексы для производительности
- [x] Скрипт инициализации с начальными данными

### В планах 📋

- [ ] Система избранного
- [ ] Жалобы на отзывы
- [ ] Премиум размещение курсов
- [ ] Email уведомления
- [ ] Поиск с автодополнением
- [ ] Сравнение курсов
- [ ] Admin панель
- [ ] API для мобильных приложений
- [ ] Интеграция с платежными системами

## Модели базы данных

### User
- Регистрация, роли (user/admin)
- Уровни пользователей
- Репутация и статистика

### Course
- Полная информация о курсе
- 5 детальных рейтингов
- Статус модерации
- Премиум размещение

### Review
- 5 критериев оценки (1-5)
- Текстовый отзыв
- Плюсы/минусы
- Рекомендация
- Статус прохождения

### Category & Subcategory
- 6 основных категорий
- Множество подкатегорий

## API Endpoints

### Auth
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `GET /api/v1/auth/me` - Текущий пользователь

### Courses
- `GET /api/v1/courses` - Список (с фильтрами)
- `GET /api/v1/courses/{id}` - Детали
- `POST /api/v1/courses` - Создать
- `PUT /api/v1/courses/{id}` - Обновить
- `DELETE /api/v1/courses/{id}` - Удалить
- `POST /api/v1/courses/{id}/approve` - Одобрить (admin)

### Reviews
- `GET /api/v1/reviews` - Список
- `POST /api/v1/reviews` - Создать
- `PUT /api/v1/reviews/{id}` - Обновить
- `DELETE /api/v1/reviews/{id}` - Удалить

### Categories
- `GET /api/v1/categories` - Список всех
- `POST /api/v1/categories` - Создать (admin)

## Команды запуска

### С Docker
```bash
make run      # Запустить все сервисы
make stop     # Остановить
make logs     # Просмотр логов
make clean    # Очистить данные
```

### Без Docker
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Порты

- **Frontend**: 3000
- **Backend API**: 8000
- **PostgreSQL**: 5432
- **Redis**: 6379
- **API Docs**: http://localhost:8000/docs

## Переменные окружения

Основные переменные в `.env`:
- `DATABASE_URL` - строка подключения к PostgreSQL
- `SECRET_KEY` - ключ для JWT
- `BACKEND_CORS_ORIGINS` - разрешенные origins
- `MAIL_*` - настройки SMTP
- `FIRST_SUPERUSER_EMAIL/PASSWORD` - админ

---

Подробная документация в README.md
