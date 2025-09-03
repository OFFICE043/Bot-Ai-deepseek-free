hereimport os
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiohttp
import asyncio

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токендер
BOT_TOKEN = os.environ.get('BOT_TOKEN') or "7457989814:AAGfKUTgDoEu9VxftnMCwjV5rCCrm6ochkQ" 
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY') or "sk-10755111f4944829ba461145b8e3dd9c"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Bot іске қосу
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("👋 salom! bot Ish lovotto!")

@dp.message_handler()Ish 
async def handle_msg(message: types.Message):
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": message.text}]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(DEEPSEEK_API_URL, json=data, headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    await message.answer(result["choices"][0]["message"]["content"])
                else:
                    await message.answer("😢 Қате пайда болды")
                    
    except Exception as e:
        logger.error(f"Қате: {e}")
        await message.answer("❌ Техникалық қате")

if __name__ == "__main__":
    logger.info("🤖 Бот іске қосылды!")
    executor.start_polling(dp, skip_updates=True)
