import os
import random
import datetime
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Загрузка токена
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Карты дня ---
# Пути к изображениям карт. Можно использовать URL или локальные пути.
CARDS = [
    {"name": "Светлая карта", "image": "https://example.com/light_card.jpg"},
    {"name": "Тёмная карта", "image": "https://example.com/dark_card.jpg"},
    {"name": "Нейтральная карта", "image": "https://example.com/neutral_card.jpg"},
]

# --- Хранилище пользовательских карт дня (в памяти) ---
USER_CARDS = {}

# --- Команды и колбэки ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🃏 Карта дня", callback_data="daily_card")],
        [InlineKeyboardButton("ℹ️ О боте", callback_data="about_bot")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать в *Домик Совы* 🦉\n\nВыберите раздел:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def about_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "*О проекте 'Домик Совы'*\n\n"
        "Это бот для самопознания и внутреннего роста. "
        "Каждый день вы можете вытягивать символическую карту, "
        "которая может подсказать вам путь на сегодня. 🃏",
        parse_mode='Markdown'
    )

# --- Карта дня ---

async def daily_card_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("✨ Вытянуть карту дня", callback_data="draw_card")]]
    
    user_id = query.from_user.id
    if user_id in USER_CARDS:
        keyboard.append([InlineKeyboardButton("📜 Мои карты дня", callback_data="my_cards")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "🔮 Добро пожаловать в раздел *Карта дня*.\nВыберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def draw_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    card = random.choice(CARDS)
    date_str = datetime.date.today().strftime('%d.%m.%Y')

    
    
    # Сохраняем карту для пользователя
    USER_CARDS.setdefault(user_id, []).append({"date": date_str, "name": card["name"], "image": card["image"]})

    await query.message.reply_photo(
        photo=card["image"],
        caption=f"🗓 {date_str}\nВаша карта дня: *{card['name']}*",
        parse_mode='Markdown'
    )

    # Обновить меню после вытягивания
    await daily_card_menu(update, context)

async def show_my_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    cards = USER_CARDS.get(user_id, [])

    if not cards:
        await query.edit_message_text("У вас пока нет карт дня.")
        return

    messages = []
    for card in cards[-5:]:  # показываем последние 5 карт
        messages.append(f"🗓 {card['date']} — *{card['name']}*")

    await query.edit_message_text(
        "*Ваши последние карты дня:*\n\n" + "\n".join(messages),
        parse_mode='Markdown'
    )

# --- Запуск ---

if __name__ == "__main__":
    print("Запуск бота Домик Совы...")
    print(f"Токен из .env: {BOT_TOKEN}")

    # Создаём event loop, если он отсутствует (актуально для Python 3.11+ на Windows)
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(daily_card_menu, pattern="^daily_card$"))
    app.add_handler(CallbackQueryHandler(draw_card, pattern="^draw_card$"))
    app.add_handler(CallbackQueryHandler(show_my_cards, pattern="^my_cards$"))
    app.add_handler(CallbackQueryHandler(about_bot, pattern="^about_bot$"))

    app.run_polling()
