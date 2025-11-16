# Telegram бот CourseRate

Telegram бот для поиска и получения информации о курсах.

## Возможности

- 🔍 Поиск курсов по названию
- 🏆 Просмотр топ курсов
- 📁 Просмотр по категориям
- 🔔 Подписка на уведомления о новых курсах
- ⭐ Просмотр рейтингов и отзывов

## Установка

```bash
cd telegram_bot

# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
echo "TELEGRAM_BOT_TOKEN=your_bot_token_here" > .env
echo "API_URL=http://localhost:8000/api/v1" >> .env
```

## Создание бота

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен и добавьте в `.env`

## Запуск

```bash
python bot.py
```

## Команды бота

- `/start` - Начать работу с ботом
- `/search <запрос>` - Поиск курсов
- `/top` - Топ-10 лучших курсов
- `/categories` - Просмотр категорий
- `/subscribe` - Подписаться на уведомления
- `/help` - Помощь

## Использование

Просто напишите название курса боту, и он найдет его для вас!

**Примеры:**
- "Python для начинающих"
- "Английский язык"
- "Веб-разработка"

## Деплой

### На Heroku

```bash
# Установка Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

heroku create your-bot-name
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set API_URL=https://your-api.com/api/v1
git push heroku main
```

### На VPS

```bash
# Создать systemd service
sudo nano /etc/systemd/system/courserate-bot.service
```

```ini
[Unit]
Description=CourseRate Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/telegram_bot
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Запуск
sudo systemctl start courserate-bot
sudo systemctl enable courserate-bot
sudo systemctl status courserate-bot
```

## Будущие функции

- [ ] Персональные рекомендации
- [ ] Сравнение курсов
- [ ] Добавление в избранное
- [ ] Напоминания о курсах
- [ ] Интеграция с оплатой
