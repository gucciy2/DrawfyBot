import os
import telebot
from telebot.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:5000')

if not BOT_TOKEN:
    print("❌ Ошибка: BOT_TOKEN не найден в .env файле!")
    print("📝 Добавьте в файл .env строку: BOT_TOKEN=ваш_токен_от_BotFather")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# ==================== КОМАНДЫ БОТА ====================

@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    """Главное меню с Web App кнопкой"""
    
    # Создаем клавиатуру с Web App кнопкой
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    web_app_btn = KeyboardButton(
        text="🎨 ОТКРЫТЬ DRAWFY",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    
    keyboard.add(web_app_btn)
    keyboard.row("🖼️ Галерея", "🛒 Магазин")
    keyboard.row("👤 Мой профиль", "❓ Помощь")
    
    # Приветственное сообщение
    welcome_text = f"""
🎨 *Добро пожаловать в Drawfy, {message.from_user.first_name}!*

*Drawfy* — это творческая платформа для рисования прямо в Telegram!

🌟 *Возможности:*
• 🎨 Рисование с разными кистями и цветами
• 🖼️ Галерея с работами других художников
• ❤️ Система лайков и комментариев
• 🛒 Магазин инструментов за монеты
• 👥 Сообщество творческих людей

📱 *Чтобы начать:* Нажмите кнопку *"🎨 ОТКРЫТЬ DRAWFY"* ниже!

🔧 *Команды:*
/start - Главное меню
/gallery - Открыть галерею
/shop - Открыть магазин
/profile - Мой профиль
/help - Помощь

✨ *Рисуйте, делитесь, вдохновляйте!*
    """
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.message_handler(commands=['gallery'])
def gallery_command(message):
    """Открыть галерею через Web App"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        "🖼️ Открыть галерею",
        web_app=WebAppInfo(url=f"{WEBAPP_URL}/gallery")
    ))
    
    bot.send_message(
        message.chat.id,
        "Открываю галерею работ... 🎨",
        reply_markup=keyboard
    )

@bot.message_handler(commands=['shop'])
def shop_command(message):
    """Открыть магазин через Web App"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        "🛒 Открыть магазин",
        web_app=WebAppInfo(url=f"{WEBAPP_URL}/shop")
    ))
    
    bot.send_message(
        message.chat.id,
        "Открываю магазин инструментов... 🎁",
        reply_markup=keyboard
    )

@bot.message_handler(commands=['profile'])
def profile_command(message):
    """Открыть профиль через Web App"""
    user_id = message.from_user.id
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        "👤 Мой профиль",
        web_app=WebAppInfo(url=f"{WEBAPP_URL}/profile?user_id={user_id}")
    ))
    
    bot.send_message(
        message.chat.id,
        "Открываю ваш профиль... 📊",
        reply_markup=keyboard
    )

@bot.message_handler(commands=['draw'])
def draw_command(message):
    """Открыть редактор рисования"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        "✏️ Начать рисовать",
        web_app=WebAppInfo(url=f"{WEBAPP_URL}/draw")
    ))
    
    bot.send_message(
        message.chat.id,
        "Открываю холст для рисования... 🎨",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda message: message.text == "🖼️ Галерея")
def gallery_button(message):
    """Обработка кнопки Галерея"""
    gallery_command(message)

@bot.message_handler(func=lambda message: message.text == "🛒 Магазин")
def shop_button(message):
    """Обработка кнопки Магазин"""
    shop_command(message)

@bot.message_handler(func=lambda message: message.text == "👤 Мой профиль")
def profile_button(message):
    """Обработка кнопки Профиль"""
    profile_command(message)

@bot.message_handler(func=lambda message: message.text == "❓ Помощь")
def help_button(message):
    """Обработка кнопки Помощь"""
    help_text = """
❓ *Помощь по Drawfy*

🎨 *Как начать:*
1. Нажмите кнопку *"🎨 ОТКРЫТЬ DRAWFY"*
2. Выберите цвет и размер кисти
3. Рисуйте на холсте
4. Сохраните работу и поделитесь!

🖼️ *Галерея:*
• Смотрите работы других художников
• Ставьте лайки ❤️
• Оставляйте комментарии 💬

🛒 *Магазин:*
• Зарабатывайте монеты за лайки
• Покупайте новые инструменты
• Открывайте особые фоны

👤 *Профиль:*
• Ваша статистика
• Ваши работы
• Достижения и уровни

💰 *Как получить монеты:*
• +10 монет за каждую новую работу
• +1 монета за каждый полученный лайк
• +50 монет за повышение уровня

📞 *Поддержка:* @drawfy_support
    """
    
    bot.send_message(
        message.chat.id,
        help_text,
        parse_mode='Markdown'
    )

# ==================== ИНЛАЙН-РЕЖИМ ====================

@bot.inline_handler(lambda query: query.query)
def inline_query(inline_query):
    try:
        # Результат 1: Открыть Drawfy
        r1 = telebot.types.InlineQueryResultArticle(
            id='1',
            title='🎨 Открыть Drawfy',
            description='Рисуй, делись работами, вдохновляй!',
            input_message_content=telebot.types.InputTextMessageContent(
                message_text='Присоединяйтесь к Drawfy! 🎨\n\nРисуйте, делитесь работами и находите вдохновение в сообществе художников!'
            ),
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    "🎨 ОТКРЫТЬ DRAWFY",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            )
        )
        
        # Результат 2: Галерея
        r2 = telebot.types.InlineQueryResultArticle(
            id='2',
            title='🖼️ Галерея Drawfy',
            description='Смотри работы других художников',
            input_message_content=telebot.types.InputTextMessageContent(
                message_text='Посмотрите удивительные работы в галерее Drawfy! 🎨'
            ),
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    "🖼️ Открыть галерею",
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}/gallery")
                )
            )
        )
        
        # Результат 3: Рисование
        r3 = telebot.types.InlineQueryResultArticle(
            id='3',
            title='✏️ Начать рисовать',
            description='Создай свой шедевр прямо сейчас!',
            input_message_content=telebot.types.InputTextMessageContent(
                message_text='Время творить! ✨\n\nОткройте Drawfy и создайте свой шедевр!'
            ),
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    "✏️ Начать рисовать",
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}/draw")
                )
            )
        )
        
        bot.answer_inline_query(inline_query.id, [r1, r2, r3], cache_time=1)
        
    except Exception as e:
        print(f"Ошибка в inline режиме: {e}")

# ==================== ЗАПУСК БОТА ====================

if __name__ == "__main__":
    print("🤖 Бот Drawfy запускается...")
    print(f"🔗 Web App URL: {WEBAPP_URL}")
    print(f"🔑 Токен: {BOT_TOKEN[:15]}...")
    print("\n📌 Бот готов к работе!")
    print("📱 Используйте команду /start в Telegram")
    print("🌐 Web App доступен по кнопке в меню бота")
    
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")