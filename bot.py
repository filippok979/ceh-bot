# bot.py - Бот ЦЕХ на aiogram для работы 24/7
import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import F

# Загружаем переменные окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "7420392791:AAF4_yGw2qHZ--aX6VTSyC5edb1zoL-9JX8")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "-4861255656")
YANDEX_DISK_LINK = os.getenv("YANDEX_DISK_LINK", "https://disk.yandex.ru/d/IeeV4DCkWstadw")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клавиатуры
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📁 Наши работы")],
        [KeyboardButton(text="💰 Рассчитать проект")],
        [KeyboardButton(text="🪵 Материалы и фурнитура")],
        [KeyboardButton(text="💬 Вопрос мастеру")]
    ],
    resize_keyboard=True
)

# Для отслеживания пользователей
user_states = {}

def get_user_info(message: types.Message):
    """Получает информацию о пользователе"""
    user = message.from_user
    return {
        'id': user.id,
        'username': user.username or 'нет username',
        'first_name': user.first_name or '',
        'last_name': user.last_name or '',
        'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip() or 'Не указано'
    }

async def notify_admin(message_text: str):
    """Уведомляет админа"""
    try:
        await bot.send_message(ADMIN_CHAT_ID, message_text)
        logger.info(f"✅ Уведомление отправлено админу")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки админу: {e}")

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    user_info = get_user_info(message)
    
    # Уведомляем админа о новом пользователе
    if user_info['id'] not in user_states:
        user_states[user_info['id']] = True
        await notify_admin(
            f"🆕 НОВЫЙ ПОЛЬЗОВАТЕЛЬ!\n"
            f"👤 {user_info['full_name']}\n"
            f"📱 @{user_info['username']}\n"
            f"🆔 ID: {user_info['id']}"
        )
    
    await message.answer(
        "Привет! Я бот мастерской «ЦЕХ» 🛠️\n"
        "Мебель на заказ по вашим размерам\n\n"
        "Выберите опцию ниже:",
        reply_markup=main_kb
    )

@dp.message(F.text == "📁 Наши работы")
async def show_works(message: types.Message):
    user_info = get_user_info(message)
    await notify_admin(f"📁 {user_info['full_name']} смотрит наши работы")
    
    await message.answer(
        f"🛠️ Наши работы:\n\n{YANDEX_DISK_LINK}\n\n"
        "Более 50+ реализованных проектов!",
        reply_markup=main_kb
    )

@dp.message(F.text == "💰 Рассчитать проект")
async def calculate_project(message: types.Message):
    user_info = get_user_info(message)
    await notify_admin(f"🚨 {user_info['full_name']} ЗАПРОСИЛ РАСЧЕТ ПРОЕКТА!")
    
    await message.answer(
        "📐 Рассчет проекта:\n\n"
        "Для точного расчета пришлите:\n"
        "• Размеры помещения\n"
        "• Эскиз или фото\n" 
        "• Пожелания по материалам\n\n"
        "📞 Свяжитесь с мастером:\n"
        "8-903-656-34-80\n"
        "@filippovceh\n\n"
        "Рассчитаем стоимость за 1 час! ⏰",
        reply_markup=main_kb
    )

@dp.message(F.text == "🪵 Материалы и фурнитура")
async def show_materials(message: types.Message):
    user_info = get_user_info(message)
    await notify_admin(f"🪵 {user_info['full_name']} смотрит материалы")
    
    await message.answer(
        "🏷️ Материалы и фурнитура:\n\n"
        "• ЛДСП Lamarty, Egger\n"
        "• Кромка Rehau\n"
        "• Фурнитура Blum, Boyard, Hafele\n"
        "• Фасады в эмали, ПВХ, FENIX\n"
        "• Натуральное дерево, шпон\n\n"
        "Все сертификаты качества в наличии! ✅",
        reply_markup=main_kb
    )

@dp.message(F.text == "💬 Вопрос мастеру")
async def ask_master(message: types.Message):
    user_info = get_user_info(message)
    await notify_admin(f"🚨 {user_info['full_name']} ЗАПРОСИЛ КОНТАКТ С МАСТЕРОМ!")
    
    await message.answer(
        "👨‍🔧 Вопрос мастеру:\n\n"
        "Свяжитесь напрямую с мастером:\n\n"
        "📞 Телефон: 8-903-656-34-80\n"
        "📱 Telegram: @filippovceh\n"
        "🏠 Мастерская: ЦЕХ\n\n"
        "Режим работы: Пн-Сб 9:00-20:00\n"
        "Ответим в течение 30 минут! 🕐",
        reply_markup=main_kb
    )

@dp.message()
async def handle_other_messages(message: types.Message):
    user_info = get_user_info(message)
    await notify_admin(f"💬 {user_info['full_name']} написал: {message.text[:50]}...")
    
    await message.answer(
        "Не понял запрос 🤔\n\n"
        "Используйте кнопки меню ниже или свяжитесь с мастером:\n"
        "📞 8-903-656-34-80\n"
        "@filippovceh",
        reply_markup=main_kb
    )

async def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Бот ЦЕХ запускается...")
    await notify_admin("✅ Бот ЦЕХ запущен в режиме 24/7 на Railway!")
    
    # Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())