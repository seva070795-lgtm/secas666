import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from google import genai
from aiohttp import web

# Логирование
logging.basicConfig(level=logging.INFO)

# Получаем ключи из переменных окружения (Render)
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", 8000))

if not BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Ошибка: Проверьте настройки BOT_TOKEN и GEMINI_API_KEY в Environment Variables на Render!")

# Инициализация клиентов
ai_client = genai.Client(api_key=GEMINI_API_KEY)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработка /start
@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}! Я твой ИИ-помощник Gemini. Задай мне любой вопрос!")

# Обработка сообщений
@dp.message()
async def chat_with_gemini(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        response = await asyncio.to_thread(
            ai_client.models.generate_content,
            model="gemini-2.5-flash",
            contents=message.text,
        )
        await message.answer(response.text)
    except Exception as e:
        logging.error(f"Ошибка Gemini: {e}")
        await message.answer("Произошла ошибка при обращении к ИИ.")

# Фейковый веб-сервер для проходимости Health Check на Render
async def handle(request):
    return web.Response(text="Bot is running!")

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
