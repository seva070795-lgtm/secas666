import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import google.generativeai as genai
from aiohttp import web

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Безопасно получаем ключи из настроек Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", 8000))

# Настраиваем классическое API Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Инициализируем бота Telegram
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Ответ на команду /start
@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}! Я твой ИИ-помощник Gemini. Задай мне любой вопрос!")

# Обработка всех текстовых сообщений
@dp.message()
async def chat_with_gemini(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        # Используем самую стабильную бесплатную модель gemini-1.5-flash через классический коннектор
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = await asyncio.to_thread(model.generate_content, message.text)
        
        await message.answer(response.text)
    except Exception as e:
        logging.error(f"Ошибка Gemini: {e}")
        await message.answer("Произошла ошибка при обращении к ИИ. Попробуйте позже.")

# Фейковый веб-сервер, чтобы Render не выдавал ошибку портов
async def handle(request):
    return web.Response(text="Бот запущен и работает!")

async def start_webhook():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

async def main():
    await start_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

