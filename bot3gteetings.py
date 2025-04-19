import os
import random
import json
import datetime
import asyncio
import telegram
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Загрузка токена из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Пути и папки ---
CARDS_DIR = "cards"
USER_CARDS_FILE = "json/cards_history.json"
PRODUCTS_FILE = "json/products.json"
ABOUT_FILE = "json/about.json"
CARDS_INFO_FILE = "json/cards_info_full.json"
USER_NAMES_FILE = "json/user_names.json"
CARD_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

# --- Загрузка и сохранение истории пользователей ---
def load_user_cards():
    if os.path.exists(USER_CARDS_FILE):
        with open(USER_CARDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_cards():
    with open(USER_CARDS_FILE, "w", encoding="utf-8") as f:
        json.dump(USER_CARDS, f, ensure_ascii=False, indent=2)

USER_CARDS = load_user_cards()

# --- Загрузка имён пользователей ---
def load_user_names():
    if os.path.exists(USER_NAMES_FILE):
        with open(USER_NAMES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_names():
    with open(USER_NAMES_FILE, "w", encoding="utf-8") as f:
        json.dump(USER_NAMES, f, ensure_ascii=False, indent=2)

USER_NAMES = load_user_names()

# --- Загрузка ресурсов ---
def load_cards():
    cards = []
    for fname in os.listdir(CARDS_DIR):
        if os.path.splitext(fname)[1].lower() in CARD_EXTENSIONS:
            cards.append({
                "name": os.path.splitext(fname)[0],
                "image_path": os.path.join(CARDS_DIR, fname)
            })
    return cards

CARDS = load_cards()


def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

PRODUCTS = load_json(PRODUCTS_FILE)
ABOUT_TEXT = load_json(ABOUT_FILE)
CARD_DESCRIPTIONS = load_json(CARDS_INFO_FILE)

# --- Приветственный экран ---
WELCOME_IMAGE_PATH = "assets/owl_welcome.png"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in USER_NAMES:
        # Приветствие с картинкой и запросом имени
        with open(WELCOME_IMAGE_PATH, "rb") as img:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=img,
                caption=(
                    "✨ Приветствую тебя, Искатель! ✨\n\n"
                    "Ты вошёл в Домик Совы — место силы, самопознания и волшебства.\n\n"
                    "Здесь ты сможешь вытягивать карту дня, исследовать свои состояния и следить за внутренними переменами.\n"
                    "А совсем скоро появятся медитации, практики и знания, которые помогут заглянуть внутрь себя.\n\n"
                    "Как тебя зовут, Искатель? Напиши своё имя ниже 👇✨"
                )
            )
        return
    await show_main_menu(update, context)

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in USER_NAMES:
        USER_NAMES[user_id] = update.message.text.strip()
        save_user_names()
        await update.message.reply_text(f"Рада познакомиться, {USER_NAMES[user_id]}! 🦉")
        await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    name = USER_NAMES.get(user_id, "Искатель")
    keyboard = [
        [InlineKeyboardButton("🃏 Карта дня", callback_data="daily_card")],
        [InlineKeyboardButton("📦 Мои продукты", callback_data="products")],
        [InlineKeyboardButton("ℹ️ О проекте", callback_data="about_project")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            f"Добро пожаловать в *Домик Совы*, {name} 🦉\n\nВыберите раздел:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            f"Добро пожаловать в *Домик Совы*, {name} 🦉\n\nВыберите раздел:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# Остальные функции (о проекте, продукты, карты и т.д.) здесь добавляются по аналогии с id5
# ...

if __name__ == "__main__":
    print("Бот запускается.")
    print(f"Токен из .env: {BOT_TOKEN}")

    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_main_menu, pattern="^start$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name))

    print("Бот запущен.")
    app.run_polling()
