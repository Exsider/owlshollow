import os 
import random
import json
import datetime
import asyncio
import telegram
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
    KeyboardButton,
    ReplyKeyboardMarkup)
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
WELCOME_IMAGE_PATH = "assets/owl_welcome.jpg"
CARDS_DIR = "cards"
USER_CARDS_FILE = "json/cards_history.json"
PRODUCTS_FILE = "json/products.json"
ABOUT_FILE = "json/about.json"
CARDS_INFO_FILE = "json/cards_info_full.json"
USER_NAMES_FILE = "json/user_names.json"
USER_PHONES_FILE = "json/user_phones.json"
CARD_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

CARDS = []
USER_CARDS = {}
USER_NAMES = {}
USER_PHONES = {}
PRODUCTS = []
ABOUT_TEXT = {}
CARD_DESCRIPTIONS = {}

def load_json_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json_file(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- Загрузка карт ---
def load_cards_from_folder():
    cards = []
    for fname in os.listdir(CARDS_DIR):
        if os.path.splitext(fname)[1].lower() in CARD_EXTENSIONS:
            cards.append({
                "name": os.path.splitext(fname)[0],
                "image_path": os.path.join(CARDS_DIR, fname)
            })
    return cards

CARDS = load_cards_from_folder()

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

# --- Загрузка телефонов пользователей ---
def load_user_phones():
    if os.path.exists(USER_PHONES_FILE):
        with open(USER_PHONES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_phones():
    with open(USER_PHONES_FILE, "w", encoding="utf-8") as f:
        json.dump(USER_PHONES, f, ensure_ascii=False, indent=2)

USER_PHONES = load_user_phones()

# --- Загрузка продуктов ---
def load_products():
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

PRODUCTS = load_products()

# --- Загрузка информации о проекте ---
def load_about():
    if os.path.exists(ABOUT_FILE):
        with open(ABOUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

ABOUT_TEXT = load_about()

# --- Загрузка описаний карт ---
def load_card_descriptions():
    if os.path.exists(CARDS_INFO_FILE):
        with open(CARDS_INFO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

CARD_DESCRIPTIONS = load_card_descriptions()

# --- Инициализация ---
CARDS = load_cards_from_folder()
USER_CARDS = load_json_file(USER_CARDS_FILE)
USER_NAMES = load_json_file(USER_NAMES_FILE)
USER_PHONES = load_json_file(USER_PHONES_FILE)
PRODUCTS = load_json_file(PRODUCTS_FILE)
ABOUT_TEXT = load_json_file(ABOUT_FILE)
CARD_DESCRIPTIONS = load_json_file(CARDS_INFO_FILE)

# --- Хендлеры ---

#--- Приветственный экран ---
async def welcome_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                    "Как тебя зовут, Искатель? Напиши своё имя ниже 👇"
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
        [InlineKeyboardButton("🔢 Рассчитать Аркан", callback_data="calculate_arkana")],
        [InlineKeyboardButton("📱 Поделиться телефоном", callback_data="share_phone")],
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

async def about_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        f"*{ABOUT_TEXT.get('title', '')}*\n\n"
        f"{ABOUT_TEXT.get('intro', '')}\n\n"
        f"{ABOUT_TEXT.get('body', '')}\n\n"
        f"_{ABOUT_TEXT.get('footer', '')}_"
    )

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="start")]]
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def products_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    messages = []
    for product in PRODUCTS:
        messages.append(
            f"*{product['name']}*\n"
            f"_{product['description']}_\n"
            f"👉 Что вы получите: {product['result']}\n"
        )

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="start")]]
    await query.edit_message_text(
        "*📦 Мои продукты:*\n\n" + "\n".join(messages),
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def daily_card_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("✨ Вытянуть карту дня", callback_data="draw_card")]]
    user_id = str(query.from_user.id)
    if user_id in USER_CARDS:
        keyboard.append([InlineKeyboardButton("🃏 Мои карты дня", callback_data="my_cards")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="start")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.edit_message_text(
            "✨ Добро пожаловать в раздел *Карта дня*.\nВыберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except telegram.error.BadRequest:
        # В случае ошибки редактирования (например, сообщение — это картинка), отправим новое
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="✨ Добро пожаловать в раздел *Карта дня*.\nВыберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def draw_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    today = datetime.date.today().strftime('%d.%m.%Y')

    user_history = USER_CARDS.get(user_id, [])
    if any(card["date"] == today for card in user_history):
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="daily_card")]]
        await query.edit_message_text(
            "😊 Вы уже вытянули карту на сегодня. Возвращайтесь завтра!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    card = random.choice(CARDS)
    card_name = card["name"]
    short_name = card_name.split(". ", 1)[-1]  # исправление
    card_description = CARD_DESCRIPTIONS.get(short_name, {}).get("description", "")

    USER_CARDS.setdefault(user_id, []).append({
        "date": today,
        "name": card_name,
        "image_path": card["image_path"]
    })

    save_user_cards()

    with open(card["image_path"], "rb") as photo:
        await query.message.reply_photo(
            photo=photo,
            caption=f"{card_description}",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="daily_card")]
           ])
        )

async def show_my_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    cards = USER_CARDS.get(user_id, [])

    if not cards:
        await query.message.reply_text("У вас пока нет карт дня.")
        return

    keyboard = [
        [InlineKeyboardButton(f"🗓 {card['date']} — {card['name']}", callback_data=f"view_card_{i}")]
        for i, card in enumerate(cards[-5:])
    ]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="daily_card")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        "*Ваши последние карты дня:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def view_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    cards = USER_CARDS.get(user_id, [])

    try:
        index = int(query.data.split('_')[-1])
        card = cards[-5:][index]
    except (IndexError, ValueError):
        await query.edit_message_text("Не удалось найти карту.")
        return

    short_name = card['name'].split(". ", 1)[-1]  # исправление
    description = CARD_DESCRIPTIONS.get(short_name, {}).get("description", "")

    with open(card["image_path"], "rb") as photo:
        await query.message.reply_photo(
            photo=photo,
            caption=f"🃏 *{card['name']}* — карта от {card['date']}\n\n{description}",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="my_cards")]])
        )
async def share_phone_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("📱 Поделиться номером", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Поделитесь своим номером телефона:", reply_markup=reply_markup)

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📲 Телефон получен!")
    user_id = update.effective_user.id
    contact = update.message.contact
    if contact:
        # Сохраняем номер телефона пользователя
        USER_PHONES[user_id] = contact.phone_number
        save_user_phones()

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
        f"Спасибо! Мы сохранили ваш номер: {contact.phone_number}",
        reply_markup=reply_markup)
    else:
        await update.message.reply_text("Пожалуйста, нажмите кнопку, чтобы поделиться номером.")

async def calculate_arkana_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Введите вашу дату рождения в формате ДД.ММ.ГГГГ:")

async def handle_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    date_text = update.message.text.strip()

    try:
        day, month, year = map(int, date_text.split("."))
        total = sum(map(int, list(f"{day:02d}{month:02d}{year}")))
        while total > 22:
            total = sum(map(int, str(total)))

        # Проверка подписки
        chat_member = await context.bot.get_chat_member(chat_id="@nady_blog", user_id=update.effective_user.id)
        if chat_member.status in ["member", "administrator", "creator"]:
            await update.message.reply_text(f"Ваш Аркан: {total} 🌟")
        else:
            await update.message.reply_text("Чтобы получить расчёт, подпишитесь на канал @nady_blog 🌀")
    except Exception:
        await update.message.reply_text("Ошибка в формате даты. Пожалуйста, введите её в виде ДД.ММ.ГГГГ")

# --- Запуск бота ---
if __name__ == "__main__":
    print("Бот запускается.")
    print(f"Токен из .env: {BOT_TOKEN}")

#  Создаём event loop, если он отсутствует (актуально для Python 3.11+ на Windows)
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", welcome_start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_phone)) 
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name))
    app.add_handler(CallbackQueryHandler(show_main_menu, pattern="^start$"))
    app.add_handler(CallbackQueryHandler(daily_card_menu, pattern="^daily_card$"))
    app.add_handler(CallbackQueryHandler(draw_card, pattern="^draw_card$"))
    app.add_handler(CallbackQueryHandler(show_my_cards, pattern="^my_cards$"))
    app.add_handler(CallbackQueryHandler(view_card, pattern="^view_card_\\d+$"))
    app.add_handler(CallbackQueryHandler(about_project, pattern="^about_project$"))
    app.add_handler(CallbackQueryHandler(products_menu, pattern="^products$"))
    app.add_handler(CallbackQueryHandler(share_phone_request, pattern="^share_phone$"))
    app.add_handler(CallbackQueryHandler(calculate_arkana_prompt, pattern="^calculate_arkana$"))

    print("Бот запущен.")
    app.run_polling()
