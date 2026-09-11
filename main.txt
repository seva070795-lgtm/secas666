import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from google import genai

# Включаем логирование, чтобы видеть работу бота в панели Render
logging.basicConfig(level=logging.INFO)

# Безопасно подтягиваем ключи из настроек Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Ответ на команду /start
@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}! "
        f"Я твой личный ИИ-помощник Gemini. Задай мне любой вопрос!"
    )

# Обработка всех текстовых сообщений пользователей
@dp.message()
async def chat_with_gemini(message: types.Message):
    # Показываем статус "печатает...", пока ИИ думает над ответом
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        # Отправляем текст пользователя в актуальную модель gemini-2.5-flash
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
        )
        # Отправляем ответ ИИ обратно пользователю в Telegram
        await message.answer(response.text)
    except Exception as e:
        logging.error(f"Ошибка Gemini: {e}")
        await message.answer("Извините, произошла ошибка при обращении к ИИ. Попробуйте чуть позже.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
