# Деплой CourseRate в Production

Руководство по развертыванию платформы на production сервере.

## Подготовка сервера

### Требования

- Ubuntu 20.04+ / Debian 11+
- 2+ CPU cores
- 4+ GB RAM
- 20+ GB SSD
- Docker и Docker Compose
- Домен (например: courserate.com)

### 1. Установка Docker

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
```

## Деплой приложения

### 2. Клонирование проекта

```bash
cd /var/www
sudo git clone <repository-url> courserate
cd courserate
sudo chown -R $USER:$USER .
```

### 3. Настройка переменных окружения

```bash
cp .env.example .env
nano .env
```

**Важные настройки для production:**

```bash
# Database (используйте сложный пароль!)
DATABASE_URL=postgresql://courseuser:STRONG_PASSWORD_HERE@db:5432/courserate
POSTGRES_PASSWORD=STRONG_PASSWORD_HERE

# JWT Security (сгенерируйте уникальный ключ)
SECRET_KEY=your-super-secret-key-min-32-characters-long-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (ваш домен)
BACKEND_CORS_ORIGINS=["https://courserate.com", "https://www.courserate.com"]

# Email (настройте SMTP)
MAIL_USERNAME=noreply@courserate.com
MAIL_PASSWORD=your-email-password
MAIL_FROM=noreply@courserate.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# Admin
FIRST_SUPERUSER_EMAIL=admin@courserate.com
FIRST_SUPERUSER_PASSWORD=CHANGE_THIS_STRONG_PASSWORD

# Environment
ENVIRONMENT=production
```

### 4. Настройка Nginx (обратный прокси)

```bash
sudo apt install nginx -y

sudo nano /etc/nginx/sites-available/courserate
```

**Конфигурация Nginx:**

```nginx
# Backend API
server {
    listen 80;
    server_name api.courserate.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 80;
    server_name courserate.com www.courserate.com;

    root /var/www/courserate/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

```bash
# Активация конфигурации
sudo ln -s /etc/nginx/sites-available/courserate /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL сертификат (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y

# Получить сертификаты
sudo certbot --nginx -d courserate.com -d www.courserate.com -d api.courserate.com

# Автоматическое обновление
sudo certbot renew --dry-run
```

### 6. Запуск приложения

```bash
# Сборка и запуск
docker-compose -f docker-compose.prod.yml up -d --build

# Инициализация БД
docker-compose exec backend python -m app.db.init_db

# Просмотр логов
docker-compose logs -f
```

### 7. Сборка Frontend

```bash
cd frontend

# Установка зависимостей
npm install

# Создание .env для production
echo "VITE_API_URL=https://api.courserate.com/api/v1" > .env

# Сборка
npm run build

# Файлы будут в /frontend/dist
```

## Production Docker Compose

Создайте `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: courserate_db_prod
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - courserate_network

  redis:
    image: redis:7-alpine
    container_name: courserate_redis_prod
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - courserate_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: courserate_backend_prod
    restart: unless-stopped
    command: gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis
    networks:
      - courserate_network

volumes:
  postgres_data:
  redis_data:

networks:
  courserate_network:
    driver: bridge
```

## Мониторинг и логи

### Настройка логирования

```bash
# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f backend

# Ротация логов
sudo nano /etc/logrotate.d/courserate
```

```
/var/log/courserate/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

### Мониторинг (опционально)

Установите Prometheus + Grafana для мониторинга.

## Резервное копирование

### Автоматический бэкап PostgreSQL

```bash
# Создать скрипт бэкапа
sudo nano /usr/local/bin/backup-courserate.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/courserate"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Бэкап БД
docker-compose exec -T db pg_dump -U courseuser courserate > $BACKUP_DIR/db_$DATE.sql

# Удалить старые бэкапы (> 7 дней)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql"
```

```bash
# Сделать исполняемым
sudo chmod +x /usr/local/bin/backup-courserate.sh

# Добавить в crontab (каждый день в 2:00)
sudo crontab -e
```

```
0 2 * * * /usr/local/bin/backup-courserate.sh
```

## Обновление приложения

```bash
# 1. Бэкап
/usr/local/bin/backup-courserate.sh

# 2. Остановка сервисов
docker-compose -f docker-compose.prod.yml down

# 3. Обновление кода
git pull origin main

# 4. Пересборка и запуск
docker-compose -f docker-compose.prod.yml up -d --build

# 5. Миграции (если есть)
docker-compose exec backend alembic upgrade head

# 6. Перезапуск nginx
sudo systemctl restart nginx
```

## Безопасность

### 1. Firewall

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Fail2Ban

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Регулярные обновления

```bash
# Автообновления безопасности
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

## Производительность

### 1. PostgreSQL тюнинг

```bash
# Редактировать postgresql.conf
docker-compose exec db bash
nano /var/lib/postgresql/data/postgresql.conf
```

Рекомендуемые настройки для 4GB RAM:
```
shared_buffers = 1GB
effective_cache_size = 3GB
work_mem = 16MB
maintenance_work_mem = 256MB
```

### 2. Redis

```bash
# Настройка максимальной памяти
docker-compose exec redis redis-cli
CONFIG SET maxmemory 512mb
CONFIG SET maxmemory-policy allkeys-lru
```

## Проверка работы

```bash
# Проверить статус сервисов
docker-compose -f docker-compose.prod.yml ps

# Проверить логи
docker-compose -f docker-compose.prod.yml logs -f

# Проверить Nginx
sudo nginx -t
sudo systemctl status nginx

# Проверить SSL
curl https://api.courserate.com/health
```

---

## Чеклист перед запуском

- [ ] Сменены все пароли по умолчанию
- [ ] Настроен SSL (HTTPS)
- [ ] Настроен SMTP для email
- [ ] Настроен Firewall
- [ ] Настроен автоматический бэкап
- [ ] Протестирован процесс обновления
- [ ] Настроен мониторинг (опционально)
- [ ] Проверены логи на ошибки

---

Удачи с деплоем! 🚀
