import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import F

# Простые настройки
BOT_TOKEN = "7420392791:AAF4_yGw2qHZ--aX6VTSyC5edb1zoL-9JX8"
ADMIN_CHAT_ID = "-4861255656"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Простая клавиатура
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📁 Наши работы")],
        [KeyboardButton(text="💰 Рассчитать проект")],
        [KeyboardButton(text="🪵 Материалы и фурнитура")],
        [KeyboardButton(text="💬 Вопрос мастеру")]
    ],
    resize_keyboard=True
)

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("Привет! Я бот ЦЕХ 🛠️", reply_markup=main_kb)
    await bot.send_message(ADMIN_CHAT_ID, f"🆕 Новый пользователь: {message.from_user.full_name}")

@dp.message(F.text == "📁 Наши работы")
async def works(message: types.Message):
    await message.answer("🛠️ Наши работы: https://disk.yandex.ru/d/IeeV4DCkWstadw", reply_markup=main_kb)

@dp.message(F.text == "💰 Рассчитать проект")
async def calculate(message: types.Message):
    await message.answer("📐 Расчет: 8-903-656-34-80 @filippovceh", reply_markup=main_kb)
    await bot.send_message(ADMIN_CHAT_ID, f"🚨 {message.from_user.full_name} запросил расчет!")

@dp.message(F.text == "🪵 Материалы и фурнитура")
async def materials(message: types.Message):
    await message.answer("🏷️ ЛДСП Lamarty, Egger • Кромка Rehau • Фурнитура Blum", reply_markup=main_kb)

@dp.message(F.text == "💬 Вопрос мастеру")
async def contact(message: types.Message):
    await message.answer("👨‍🔧 Контакты: 8-903-656-34-80 @filippovceh", reply_markup=main_kb)
    await bot.send_message(ADMIN_CHAT_ID, f"🚨 {message.from_user.full_name} запросил контакт!")

@dp.message()
async def other_messages(message: types.Message):
    await message.answer("Используйте кнопки меню 👇", reply_markup=main_kb)

async def main():
    print("🚀 Бот ЦЕХ запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
