import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
import aiohttp
import json

# Токендерді осы жерге енгізіңіз
BOT_TOKEN = "8302815646:AAGAQF_XxXtMm8XEEdnPrnt8EwqJBLghnaU"
DEEPSEEK_API_KEY = "sk-10755111f4944829ba461145b8e3dd9c"  # Сіздің API кілтіңіз
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Bot, Dispatcher және Router іске қосу
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Логирование
logging.basicConfig(level=logging.INFO)

# /start командасы
@router.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Салем! Мен DeepSeek ботиман. Сизга кандай ёрдам бера оламан?")

# Барлык хабарламаларға жауап беру
@router.message()
async def handle_message(message: types.Message):
    user_text = message.text

    # DeepSeek API-га запрос жіберу
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",  # DeepSeek моделі
        "messages": [{"role": "user", "content": user_text}],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(DEEPSEEK_API_URL, json=data, headers=headers) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    bot_response = response_data["choices"][0]["message"]["content"]
                else:
                    bot_response = "❌ Қателік пайда болды. API жауап бермейді."

    except Exception as e:
        bot_response = f"❌ Қате: {str(e)}"

    # Жауапты жіберу
    await message.answer(bot_response)

# Ботты іске қосу
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
