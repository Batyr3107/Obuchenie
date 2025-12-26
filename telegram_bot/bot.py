"""
Telegram бот для платформы CourseRate
Позволяет искать курсы, получать уведомления и подписываться на новые курсы
"""
import os
import asyncio
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Настройки
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
REQUEST_TIMEOUT = 10  # Таймаут для HTTP запросов в секундах

# Logger
logger = logging.getLogger(__name__)


# ============ КОМАНДЫ ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    welcome_message = """
🎓 **Добро пожаловать в CourseRate!**

Я помогу вам найти лучшие обучающие курсы.

**Доступные команды:**
/search - Поиск курсов
/top - Топ курсов
/categories - Категории курсов
/help - Помощь

Просто напишите название курса, и я найду его для вас!
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = """
📚 **Как пользоваться ботом:**

1️⃣ **Поиск курса**
   Просто напишите название или используйте /search

2️⃣ **Топ курсы**
   Используйте /top чтобы увидеть лучшие курсы

3️⃣ **Категории**
   /categories - просмотр всех категорий

4️⃣ **Уведомления**
   /subscribe - подписаться на новые курсы

**Примеры:**
• "Python для начинающих"
• "Веб-разработка"
• "Английский язык"
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def search_courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /search"""
    if not context.args:
        await update.message.reply_text(
            "Использование: /search <название курса>\nНапример: /search Python"
        )
        return

    query = ' '.join(context.args)
    await handle_search(update, query)


async def top_courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /top - топ курсы"""
    try:
        response = requests.get(f"{API_URL}/courses?limit=10&min_rating=4.5", timeout=REQUEST_TIMEOUT)
        courses = response.json()

        if not courses:
            await update.message.reply_text("Курсы не найдены 😕")
            return

        message = "🏆 **Топ-10 курсов:**\n\n"
        for i, course in enumerate(courses, 1):
            stars = "⭐" * int(course.get('avg_rating', 0))
            message += f"{i}. **{course['title']}**\n"
            message += f"   {stars} {course.get('avg_rating', 0):.1f}/5\n"
            message += f"   💬 {course.get('total_reviews', 0)} отзывов\n\n"

        # Кнопки
        keyboard = [[InlineKeyboardButton("🌐 Открыть сайт", url="https://courserate.com/courses")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")


async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /categories"""
    try:
        response = requests.get(f"{API_URL}/categories", timeout=REQUEST_TIMEOUT)
        categories_list = response.json()

        message = "📁 **Категории курсов:**\n\n"
        for cat in categories_list:
            message += f"• {cat['name']}\n"

        keyboard = [
            [InlineKeyboardButton(cat['name'], callback_data=f"cat_{cat['id']}")]
            for cat in categories_list[:6]  # Первые 6
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")


# ============ ОБРАБОТКА ТЕКСТА ============

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений (поиск)"""
    query = update.message.text
    await handle_search(update, query)


async def handle_search(update: Update, query: str):
    """Поиск курсов"""
    try:
        # Поиск через API
        response = requests.get(f"{API_URL}/courses?search={query}&limit=5", timeout=REQUEST_TIMEOUT)
        courses = response.json()

        if not courses:
            await update.message.reply_text(
                f"Курсы по запросу '{query}' не найдены 😕\n\nПопробуйте:\n• Изменить запрос\n• Использовать /categories"
            )
            return

        message = f"🔍 **Найдено курсов: {len(courses)}**\n\n"

        for course in courses:
            stars = "⭐" * int(course.get('avg_rating', 0))
            price = "💰 Бесплатно" if course.get('price_type') == 'free' else f"💵 {course.get('price_amount')} {course.get('currency')}"

            message += f"**{course['title']}**\n"
            message += f"{stars} {course.get('avg_rating', 0):.1f}/5 ({course.get('total_reviews', 0)} отзывов)\n"
            message += f"{price}\n"
            message += f"/course_{course['id']}\n\n"

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"Ошибка поиска: {str(e)}")


# ============ CALLBACK ОБРАБОТЧИКИ ============

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка callback кнопок"""
    query = update.callback_query
    await query.answer()

    data = query.data

    # Категория
    if data.startswith("cat_"):
        category_id = data.split("_")[1]
        try:
            response = requests.get(f"{API_URL}/courses?category_id={category_id}&limit=10", timeout=REQUEST_TIMEOUT)
            courses = response.json()

            message = f"📚 **Курсы в категории:**\n\n"
            for course in courses[:5]:
                message += f"• {course['title']} (⭐ {course.get('avg_rating', 0):.1f})\n"

            await query.edit_message_text(message, parse_mode='Markdown')

        except Exception as e:
            await query.edit_message_text(f"Ошибка: {str(e)}")


# ============ ПОДПИСКИ И УВЕДОМЛЕНИЯ ============

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подписаться на уведомления"""
    user = update.effective_user

    try:
        # Отправляем запрос на API для сохранения подписчика
        subscriber_data = {
            "telegram_user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "notify_new_courses": True,
            "notify_top_courses": True,
            "notify_special_offers": False
        }

        response = requests.post(f"{API_URL}/telegram/subscribe", json=subscriber_data, timeout=REQUEST_TIMEOUT)

        if response.status_code == 201:
            await update.message.reply_text(
                "✅ Вы подписались на уведомления!\n\nВы будете получать:\n• Новые топ курсы\n• Обновления рейтингов\n• Специальные предложения"
            )
        elif response.status_code == 400 and "уже активна" in response.text:
            await update.message.reply_text(
                "ℹ️ Вы уже подписаны на уведомления!"
            )
        else:
            await update.message.reply_text(
                "⚠️ Не удалось подписаться. Попробуйте позже."
            )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка подписки: {str(e)}\n\nПопробуйте позже."
        )


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отписаться от уведомлений"""
    user_id = update.effective_user.id

    try:
        # Отправляем запрос на API для отписки
        response = requests.post(f"{API_URL}/telegram/unsubscribe/{user_id}", timeout=REQUEST_TIMEOUT)

        if response.status_code == 200:
            await update.message.reply_text("❌ Вы отписались от уведомлений.")
        elif response.status_code == 404:
            await update.message.reply_text("ℹ️ Вы не были подписаны на уведомления.")
        else:
            await update.message.reply_text("⚠️ Не удалось отписаться. Попробуйте позже.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка отписки: {str(e)}\n\nПопробуйте позже.")


# ============ MAIN ============

def main():
    """Запуск бота"""
    logger.info("Starting Telegram bot CourseRate...")

    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_courses))
    application.add_handler(CommandHandler("top", top_courses))
    application.add_handler(CommandHandler("categories", categories))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))

    # Текстовые сообщения
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Callback кнопки
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Запуск
    logger.info("Telegram bot started successfully!")
    application.run_polling()


if __name__ == "__main__":
    main()
