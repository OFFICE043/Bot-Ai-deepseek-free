import os
import logging
import random
import time
from datetime import datetime
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiohttp
import asyncio
import json
from flask import Flask
from threading import Thread

# ================== KEEP_ALIVE ҮШІН ================== #
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 AnimeAI Bot is Alive! 🎌"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = Thread(target=run_flask)
    thread.daemon = True
    thread.start()

# ================== .env ЖҮКТЕУ ================== #
from dotenv import load_dotenv
load_dotenv()  # .env файлын ең бірінші жүктеу!

# ================== КОНФИГУРАЦИЯ ================== #
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Токендер
BOT_TOKEN = os.environ.get('BOT_TOKEN') or "8302815646:AAH6fR8n6f5s7d8f9g0h1j2k3l4m5n6o7p8q"
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY') or "sk-10755111f4944829ba461145b8e3dd9c"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Bot іске қосу
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ================== КЕЙІПКЕРЛЕР ================== #
class AnimeStates(StatesGroup):
    waiting_for_anime_name = State()

# ================== КӘЛКЕЛІ ЖАУАПТАР ================== #
FUNNY_RESPONSES = [
    "🤔 Біраз ойланайын...",
    "🎌 Аниме детективі жұмыс істеп тұр!",
    "📺 Экранді іздеу режимінде...",
    "🍥 Рамен ішіп, ойланамын...",
    "🎮 Жеңілдік кодын іздеуде...",
    "🔍 Аниме іздеу базасын сканерлеуде..."
]

ANIME_FACTS = [
    "🎎 Аниме сөзі 'анимация' деген сөзден шыққан!",
    "📊 Жапонияда 400-ден астам аниме студия бар!",
    "🏆 'Spirited Away' Оскар марапатын жеңіп алған тұңғыш аниме!",
    "🎵 Көптеген анимелердің саундтректері чарттарды басып озған!",
    "🌍 Аниме әлемде 100-ден астам елдерде көрсетіледі!"
]

# ================== ИНЛАЙН ТҮЙМЕЛЕР ================== #
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("🎌 Аниме туралы", callback_data="anime_info"),
        InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        InlineKeyboardButton("🎮 Көмек", callback_data="help"),
        InlineKeyboardButton("❤️ Ұнайды", callback_data="like")
    ]
    keyboard.add(*buttons)
    return keyboard

# ================== КОМАНДАЛАР ================== #
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user = message.from_user
    welcome_text = f"""
🎊 <b>Сәлем, {user.first_name}!</b>

🤖 Мен <b>AnimeAI ботпын</b>! Мен сізге:
• 🎌 Аниме туралы ақпарат беремін
• 📺 Кеңестер ұсынамын  
• 🎎 Көңілді фактілер айтамын
• 🔍 Кез келген сұрақтарға жауап беремін

✨ Жай ғана хабарлама жіберіңіз!
    """
    await message.answer(welcome_text, reply_markup=get_main_keyboard())
    logger.info(f"Пайдаланушы {user.id} ботты іске қосты")

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    help_text = """
🆘 <b>Көмек бөлімі:</b>

• <b>Аниме туралы сұрақтар:</b>
  - "Naruto туралы айт"
  - "One Piece кейіпкерлері"
  - "Ұсынатын анимелер"

• <b>Жалпы сұрақтар:</b>
  - Кез келген тақырыпта сұрақ қоя аласыз!

• <b>Арнайы командалар:</b>
  /start - Ботты қайта іске қосу
  /help - Көмек алу
  /stats - Статистиканы көру

🎯 <b>Мысал сұрақтар:</b>
• "Attack on Titan синопсисі"
• "Studio Ghibli фильмдері" 
• "Ең үздік романтикалық анимелер"
    """
    await message.answer(help_text)

@dp.message_handler(commands=['stats'])
async def stats_command(message: types.Message):
    stats_text = f"""
📊 <b>Бот статистикасы:</b>

• 🕐 Бот іске қосылған уақыт: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• 🤖 Паидаланушылар: Көп! 
• 🎌 Анимелер базасы: 1000+ 
• ⚡ Жұмыс режимі: Белсенді

🔧 <b>Техникалық ақпарат:</b>
• 🤖 AI: DeepSeek
• 🐍 Тіл: Python 3.11
• 📚 Кітапхана: Aiogram 2.25
    """
    await message.answer(stats_text)

# ================== ИНЛАЙН ТҮЙМЕЛЕР ================== #
@dp.callback_query_handler(lambda c: c.data == 'anime_info')
async def anime_info_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        "🎌 <b>Аниме ақпараты:</b>\n\nАниме туралы кез келген сұрақ қоя аласыз! Мысалы:\n• 'Naruto синопсисі'\n• 'Ең үздік анимелер'\n• 'Жапония мультфильмдері'",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query_handler(lambda c: c.data == 'stats')
async def stats_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await stats_command(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == 'help')
async def help_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await help_command(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == 'like')
async def like_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, "❤️ Рахмет!")
    await bot.send_message(
        callback_query.from_user.id,
        "❤️ <b>Рахмет қолдауыңыз үшін!</b>\n\nБотты жақсартуға көмектесу үшін кез келген пікіріңізді жіберіңіз!",
        reply_markup=get_main_keyboard()
    )

# ================== НЕГІЗГІ ХАБАРЛАМАЛАР ================== #
@dp.message_handler()
async def handle_all_messages(message: types.Message):
    try:
        user_text = message.text.strip()
        user_id = message.from_user.id
        
        # Көңілді жауап беру
        funny_response = random.choice(FUNNY_RESPONSES)
        wait_msg = await message.answer(f"{funny_response}...")
        
        # Кейде көңілді факті қосу
        if random.random() < 0.1:  # 10% ықтималдық
            fact = random.choice(ANIME_FACTS)
            await message.answer(f"💡 <b>Білесіз бе?</b>\n\n{fact}")

        # DeepSeek API-ге сұрау
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{
                "role": "user", 
                "content": f"Сәлем! Менің сұрағым: {user_text}. Өзбек және орыс тілдерінде жауап бер."
            }],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(DEEPSEEK_API_URL, json=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    bot_response = response_data["choices"][0]["message"]["content"]
                    
                    # Жауапты бөлу (егер тым ұзын болса)
                    if len(bot_response) > 4000:
                        parts = [bot_response[i:i+4000] for i in range(0, len(bot_response), 4000)]
                        for part in parts:
                            await message.answer(part)
                    else:
                        await message.answer(bot_response)
                    
                    # Күту хабарламасын өшіру
                    await bot.delete_message(message.chat.id, wait_msg.message_id)
                    
                    logger.info(f"Пайдаланушы {user_id} сәтті жауап алды")
                    
                else:
                    error_msg = await response.text()
                    await message.answer("❌ <b>Қате пайда болды:</b>\n\nAPI жауап бермейді. Кейінірек қайталаңыз.")
                    logger.error(f"API қатесі: {response.status} - {error_msg}")

    except Exception as e:
        logger.error(f"Жалпы қате: {e}")
        await message.answer("❌ <b>Техникалық қате пайда болды:</b>\n\nКейінірек қайталап көріңіз.")

# ================== БОТТЫ ІСКЕ ҚОСУ ================== #
async def on_startup(dp):
    logger.info("✅ Бот сәтті іске қосылды!")
    try:
        await bot.send_message(8302815646, "🚀 Бот іске қосылды!")
    except:
        pass

async def on_shutdown(dp):
    logger.warning("❌ Бот өшіруде...")
    await bot.close()

if __name__ == "__main__":
    # Keep_alive іске қосу
    keep_alive()
    logger.info("🌐 Keep_alive сервері іске қосылды!")
    
    logger.info("🤖 AnimeAI бот іске қосылуда...")
    executor.start_polling(
        dp, 
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
)
