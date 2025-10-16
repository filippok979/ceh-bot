import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import F
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📁 Наши работы")],
        [KeyboardButton(text="💰 Рассчитать проект")],
        [KeyboardButton(text="🪵 Материалы и фурнитура")],
        [KeyboardButton(text="💬 Вопрос мастеру")]
    ],
    resize_keyboard=True
)

async def notify_admin(message_text: str):
    """Отправляет полное уведомление админу"""
    try:
        await bot.send_message(ADMIN_CHAT_ID, message_text)
        print(f"✅ Уведомление отправлено: {message_text}")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

@dp.message(F.text == "/start")
async def start(message: types.Message):
    user = message.from_user
    await message.answer("Привет! Я бот ЦЕХ 🛠️ Выберите опцию:", reply_markup=main_kb)
    
    # Полное уведомление админу
    user_info = f"👤 {user.full_name} (@{user.username})" if user.username else f"👤 {user.full_name}"
    await notify_admin(f"🆕 НОВЫЙ ПОЛЬЗОВАТЕЛЬ!\n{user_info}\n🆔 ID: {user.id}\n⏰ {datetime.now().strftime('%H:%M %d.%m.%Y')}")

@dp.message(F.text == "📁 Наши работы")
async def works(message: types.Message):
    await message.answer("🛠️ Наши работы: https://disk.yandex.ru/d/IeeV4DCkWstadw", reply_markup=main_kb)
    await notify_admin(f"📁 {message.from_user.full_name} посмотрел наши работы")

@dp.message(F.text == "💰 Рассчитать проект")
async def calculate(message: types.Message):
    await message.answer("📐 Расчет: 8-903-656-34-80 @filippovceh", reply_markup=main_kb)
    await notify_admin(f"🚨 ЗАПРОС РАСЧЕТА!\n👤 {message.from_user.full_name}\n⏰ {datetime.now().strftime('%H:%M %d.%m.%Y')}")

@dp.message(F.text == "🪵 Материалы и фурнитура")
async def materials(message: types.Message):
    await message.answer("🏷️ ЛДСП Lamarty, Egger • Кромка Rehau • Фурнитура Blum", reply_markup=main_kb)
    await notify_admin(f"🪵 {message.from_user.full_name} посмотрел материалы")

@dp.message(F.text == "💬 Вопрос мастеру")
async def contact(message: types.Message):
    await message.answer("👨‍🔧 Контакты: 8-903-656-34-80 @filippovceh", reply_markup=main_kb)
    await notify_admin(f"🚨 ЗАПРОС КОНТАКТА!\n👤 {message.from_user.full_name}\n⏰ {datetime.now().strftime('%H:%M %d.%m.%Y')}")

@dp.message()
async def handle_other_messages(message: types.Message):
    """Обработка ЛЮБЫХ других сообщений"""
    user = message.from_user
    text = message.text or "📷 [фото/файл/стикер]"
    
    # Отправляем полный текст пользователю
    await message.answer("Используйте кнопки меню 👇", reply_markup=main_kb)
    
    # Отправляем ПОЛНОЕ уведомление админу
    user_info = f"👤 {user.full_name} (@{user.username})" if user.username else f"👤 {user.full_name}"
    full_notification = (
        f"💬 СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ\n"
        f"{user_info}\n"
        f"🆔 ID: {user.id}\n"
        f"📝 Текст: {text}\n"
        f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
    )
    
    await notify_admin(full_notification)

async def main():
    print("🚀 Бот ЦЕХ запущен!")
    await notify_admin("✅ Бот ЦЕХ запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
