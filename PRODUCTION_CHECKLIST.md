# Production Deployment Checklist

## ✅ Выполнено

### Безопасность
- [x] Добавлена валидация и санитизация входных данных (validators.py)
- [x] Реализован rate limiting для защиты от DDoS и brute-force атак
- [x] Добавлена защита от XSS (HTML санитизация с bleach)
- [x] Добавлена защита от SQL injection (валидация запросов)
- [x] Используется ORM (SQLAlchemy) для безопасной работы с БД
- [x] JWT токены для аутентификации
- [x] Хеширование паролей (bcrypt)

### Производительность
- [x] Добавлены индексы на внешние ключи (Review, Favorite, Report)
- [x] Пагинация для списков курсов и отзывов
- [x] Индексы на поля статусов для быстрой фильтрации

### Обработка ошибок
- [x] Error Boundary в React для отлова ошибок рендеринга
- [x] HTTP exception обработка в FastAPI

### Тестирование
- [x] Базовые API тесты (test_api.py)
- [x] Тесты валидаторов (test_validators.py)
- [x] Pytest fixtures для тестовой БД

---

## 🔴 Критически важно перед деплоем

### Безопасность и конфигурация
- [ ] **Изменить SECRET_KEY в production**
  - Сгенерировать криптографически стойкий ключ
  - Хранить в переменных окружения, НИКОГДА не в коде

- [ ] **Настроить CORS правильно**
  - Заменить `allow_origins=["*"]` на конкретные домены
  - Пример: `allow_origins=["https://yourdomain.com"]`

- [ ] **Создать .env файл для production**
  ```bash
  # Backend .env
  DATABASE_URL=postgresql://user:password@host:5432/dbname
  SECRET_KEY=your-very-secure-secret-key-here
  ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
  DEBUG=False

  # Email settings
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USER=your-email@gmail.com
  SMTP_PASSWORD=your-app-password

  # Telegram Bot
  TELEGRAM_BOT_TOKEN=your-bot-token

  # Frontend .env
  VITE_API_URL=https://api.yourdomain.com
  ```

- [ ] **Добавить .env файлы в .gitignore**

- [ ] **Настроить HTTPS/SSL**
  - Получить SSL сертификат (Let's Encrypt)
  - Настроить редирект HTTP → HTTPS
  - Включить HSTS заголовки

### База данных
- [ ] **Настроить production БД**
  - Использовать PostgreSQL вместо SQLite
  - Настроить регулярные бэкапы
  - Настроить connection pooling

- [ ] **Выполнить миграции БД**
  ```bash
  # Установить alembic
  pip install alembic

  # Инициализировать
  alembic init alembic

  # Создать миграцию
  alembic revision --autogenerate -m "Initial migration"

  # Применить
  alembic upgrade head
  ```

### Rate Limiting
- [ ] **Переключить на Redis для rate limiting**
  ```python
  # В rate_limit.py заменить:
  storage_uri="memory://"  # Текущее
  # На:
  storage_uri="redis://localhost:6379"  # Production
  ```

- [ ] **Установить и настроить Redis**
  ```bash
  # Docker compose
  services:
    redis:
      image: redis:alpine
      ports:
        - "6379:6379"
  ```

### Логирование и мониторинг
- [ ] **Настроить логирование**
  ```python
  # В main.py добавить:
  import logging
  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
      handlers=[
          logging.FileHandler('app.log'),
          logging.StreamHandler()
      ]
  )
  ```

- [ ] **Добавить мониторинг ошибок** (Sentry)
  ```bash
  pip install sentry-sdk[fastapi]
  ```

- [ ] **Настроить логирование admin действий**
  - Логировать все изменения статусов курсов
  - Логировать блокировку/разблокировку пользователей
  - Логировать удаление контента

### Frontend
- [ ] **Оптимизировать production build**
  ```bash
  # В vite.config.js добавить:
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Удалить console.log в production
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
        },
      },
    },
  }
  ```

- [ ] **Настроить code splitting**
  - Lazy loading для роутов
  - Динамические импорты для тяжелых компонентов

- [ ] **Добавить Service Worker** (опционально для PWA)

### Docker
- [ ] **Создать production Dockerfile**
  ```dockerfile
  # Backend
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

  # Frontend
  FROM node:18-alpine as build
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci
  COPY . .
  RUN npm run build

  FROM nginx:alpine
  COPY --from=build /app/dist /usr/share/nginx/html
  COPY nginx.conf /etc/nginx/nginx.conf
  ```

- [ ] **Оптимизировать docker-compose.yml**
  - Добавить health checks
  - Настроить restart policies
  - Добавить resource limits

### Тестирование
- [ ] **Запустить все тесты**
  ```bash
  cd backend
  pytest -v
  ```

- [ ] **Провести нагрузочное тестирование**
  ```bash
  # Установить locust
  pip install locust

  # Создать locustfile.py и запустить
  locust -f locustfile.py
  ```

- [ ] **Проверить на уязвимости**
  ```bash
  # Python зависимости
  pip install safety
  safety check

  # NPM зависимости
  npm audit
  ```

---

## 🟡 Желательно перед деплоем

### Функциональность
- [ ] **Добавить email верификацию**
  - Отправка письма при регистрации
  - Подтверждение email перед активацией аккаунта

- [ ] **Реализовать восстановление пароля**
  - Endpoint для запроса сброса
  - Email с временной ссылкой
  - Страница для установки нового пароля

- [ ] **Добавить 2FA** (опционально)

### Производительность
- [ ] **Настроить кэширование**
  ```python
  from fastapi_cache import FastAPICache
  from fastapi_cache.backends.redis import RedisBackend

  # В main.py
  @app.on_event("startup")
  async def startup():
      redis = aioredis.from_url("redis://localhost")
      FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

  # В endpoints
  @cache(expire=3600)
  async def get_courses(...):
      ...
  ```

- [ ] **Оптимизировать N+1 queries**
  - Использовать `joinedload()` для связанных данных
  - Проверить все запросы с помощью SQLAlchemy echo

- [ ] **Добавить CDN для статики**
  - Изображения курсов
  - JS/CSS файлы
  - Шрифты

### Мониторинг и аналитика
- [ ] **Интегрировать Google Analytics** (опционально)

- [ ] **Настроить uptime мониторинг**
  - UptimeRobot или аналог
  - Алерты при падении сервиса

- [ ] **Настроить мониторинг производительности**
  - New Relic / DataDog / Prometheus
  - Метрики: response time, error rate, throughput

### UX улучшения
- [ ] **Добавить loading states везде**
  - Skeleton loaders для списков
  - Спиннеры для кнопок
  - Progress bars для форм

- [ ] **Улучшить SEO**
  - Meta tags для всех страниц
  - Open Graph tags
  - Sitemap.xml
  - robots.txt

- [ ] **Добавить offline mode** (PWA)

---

## 📋 После деплоя

### Мониторинг
- [ ] Проверить все эндпоинты вручную
- [ ] Проверить работу email уведомлений
- [ ] Проверить работу Telegram бота
- [ ] Мониторить логи первые 24 часа

### Документация
- [ ] Обновить README.md с production инструкциями
- [ ] Создать документацию для API (Swagger автоматически)
- [ ] Документация для админов

### Юридическое
- [ ] Политика конфиденциальности
- [ ] Пользовательское соглашение
- [ ] Cookie policy (если используются)

---

## 🔧 Полезные команды

### Development
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

# Tests
cd backend
pytest -v --cov=app
```

### Production
```bash
# Build
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Database backup
docker exec postgres pg_dump -U user dbname > backup.sql

# Database restore
docker exec -i postgres psql -U user dbname < backup.sql
```

---

## 📞 Support contacts

- Sentry: https://sentry.io/
- Redis Cloud: https://redis.com/
- PostgreSQL hosting: https://www.postgresql.org/support/professional_hosting/
- SSL certificates: https://letsencrypt.org/

---

**Last updated:** 2025-11-16
