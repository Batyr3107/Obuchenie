# Database Migration Guide

## Создание Initial Migration

После внесения всех изменений в модели (включая новую модель `TelegramSubscriber`), необходимо создать миграцию базы данных.

### Шаги:

1. **Убедитесь, что база данных запущена:**
   ```bash
   docker-compose up -d postgres
   ```

2. **Перейдите в директорию backend:**
   ```bash
   cd backend
   ```

3. **Создайте автоматическую миграцию:**
   ```bash
   alembic revision --autogenerate -m "Initial migration with all models including TelegramSubscriber"
   ```

4. **Проверьте созданный файл миграции:**
   ```bash
   # Файл будет создан в backend/alembic/versions/
   ls alembic/versions/
   ```

5. **Примените миграцию:**
   ```bash
   alembic upgrade head
   ```

6. **Проверьте статус миграции:**
   ```bash
   alembic current
   ```

### Что включено в миграцию:

✅ **Модели с database indexes:**
- `User` - email, role indexes
- `Course` - slug, status, category indexes
- `Review` - user_id, course_id, created_at indexes ✨
- `Favorite` - user_id, course_id, created_at indexes ✨
- `Report` - user_id, review_id, status indexes ✨
- `Category` - name, slug indexes
- `Tag` - name index
- `PremiumPlacement` - course_id, tier indexes

✅ **Новая модель:**
- `TelegramSubscriber` - для управления подписками Telegram бота

### Откат миграции (если нужно):

```bash
# Откатить последнюю миграцию
alembic downgrade -1

# Откатить все миграции
alembic downgrade base
```

### Проверка состояния БД:

```bash
# Подключиться к PostgreSQL
docker-compose exec postgres psql -U courserate -d courserate_db

# Посмотреть все таблицы
\dt

# Посмотреть индексы для конкретной таблицы
\d reviews
\d favorites
\d reports
\d telegram_subscribers

# Выйти
\q
```

### Важные замечания:

1. **Перед созданием миграции** убедитесь, что все модели импортированы в `backend/app/db/base.py`
2. **Всегда проверяйте** сгенерированный файл миграции перед применением
3. **Делайте backup** базы данных перед применением миграций в production
4. **Используйте транзакции** для критических миграций

### Production Checklist:

- [ ] Создана миграция
- [ ] Миграция протестирована на dev окружении
- [ ] Создан backup production базы
- [ ] Миграция применена в production
- [ ] Проверена целостность данных
- [ ] Проверена производительность с новыми индексами

## Troubleshooting

### Проблема: "Target database is not up to date"

```bash
alembic stamp head
```

### Проблема: "Can't locate revision identified by..."

```bash
# Пересоздайте миграцию
rm alembic/versions/*.py
alembic revision --autogenerate -m "Fresh migration"
```

### Проблема: База данных не отвечает

```bash
# Перезапустите контейнер
docker-compose restart postgres

# Проверьте логи
docker-compose logs postgres
```
