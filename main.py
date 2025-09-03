import os
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiohttp
import json
from dotenv import load_dotenv

# .env файлын жүктеу
load_dotenv()

# Токендерді алу
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Логирование құру
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot және Dispatcher құру
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# /start командасы
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    try:
        welcome_text = (
            "👋 Салем! Мен DeepSeek ботиман!\n\n"
            "Мен сізге келесілерде көмектесе аламын:\n"
            "• Аниме туралы ақпарат беру\n"
            "• Сұрақтарға жауап беру\n"
            "• Әр түрлі тақырыптарда сөйлесу\n\n"
            "Жай ғана хабарлама жазыңыз!"
        )
        await message.answer(welcome_text)
        logger.info(f"Пайдаланушы {message.from_user.id} /start басты")
    except Exception as e:
        logger.error(f"/start қатесі: {e}")

# /help командасы
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    help_text = (
        "🆘 Көмек\n\n"
        "Мен сізге әр түрлі сұрақтарға жауап бере аламын:\n"
        "• Аниме туралы ақпарат\n"
        "• Көркем әдебиет\n"
        "• Технологиялар\n"
        "• Және басқа да көптеген тақырыптар\n\n"
        "Жай ғана өз сұрағыңызды жазыңыз!"
    )
    await message.answer(help_text)

# Барлық хабарламаларға жауап беру
@dp.message_handler()
async def handle_all_messages(message: types.Message):
    try:
        # Хабарламаны тексеру
        if not message.text or message.text.strip() == "":
            await message.answer("📝 Маған бірдеңе жазсаңызшы!")
            return

        user_text = message.text.strip()
        user_id = message.from_user.id
        username = message.from_user.username or "белгісіз"
        
        logger.info(f"Пайдаланушы {user_id} (@{username}): {user_text}")

        # DeepSeek API-га запрос дайындау
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": user_text}],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        # API-га запрос жіберу
        async with aiohttp.ClientSession() as session:
            async with session.post(DEEPSEEK_API_URL, json=data, headers=headers) as response:
                
                if response.status == 200:
                    response_data = await response.json()
                    bot_response = response_data["choices"][0]["message"]["content"]
                    
                    # Жауаптың ұзындығын тексеру
                    if len(bot_response) > 4000:
                        bot_response = bot_response[:4000] + "..."
                    
                    await message.answer(bot_response)
                    logger.info(f"Бот жауап берді: {bot_response[:100]}...")
                
                elif response.status == 401:
                    await message.answer("🔑 API кілті жарамсыз. Байланыстырыңыз: @admin")
                    logger.error("API кілті жарамсыз")
                
                elif response.status == 429:
                    await message.answer("⏰ Шамадан тыс көп сұраулар. Біраздан кейін қайталаңыз.")
                    logger.warning("Шамадан тыс көп сұраулар")
                
                else:
                    error_text = await response.text()
                    await message.answer("❌ API қатесі. Кейінірек қайталаңыз.")
                    logger.error(f"API қатесі: {response.status} - {error_text}")

    except aiohttp.ClientError as e:
        await message.answer("🌐 Желі қатесі. Интернет байланысын тексеріңіз.")
        logger.error(f"Желі қатесі: {e}")
    
    except Exception as e:
        await message.answer("❌ Ішкі қате пайда болды. Кейінірек қайталаңыз.")
        logger.error(f"Жалпы қате: {e}")

# Ботты іске қосу
if __name__ == "__main__":
    try:
        logger.info("=== БОТ ІСКЕ ҚОСЫЛУДА ===")
        logger.info(f"Bot Token: {BOT_TOKEN[:10]}...")
        logger.info(f"API Key: {DEEPSEEK_API_KEY[:10]}...")
        
        executor.start_polling(
            dp,
            skip_updates=True,
            timeout=60,
            relax=0.1
        )
        
    except Exception as e:
        logger.critical(f"Ботты іске қосу қатесі: {e}")
