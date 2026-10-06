from aiogram import Bot, Dispatcher
import asyncio
import logging
from config import TOKEN
from handlers import start, menu, cart, admin

# Loggingni yoqish
import logging.handlers
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(BASE_DIR / 'bot_error.log', maxBytes=5000000, backupCount=3),
        logging.StreamHandler()
    ]
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Routers
dp.include_router(start.router)
dp.include_router(menu.router)
dp.include_router(cart.router)
dp.include_router(admin.router)


import os
import aiohttp

async def keep_alive():
    """Serverni uxlab qolmasligi uchun har 10 minutda ping qilib turadi."""
    url = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if not url:
        logging.warning("RENDER_EXTERNAL_HOSTNAME topilmadi, keep_alive ishlamaydi.")
        return
    
    ping_url = f"https://{url}/ping/"
    logging.info(f"Keep-alive boshlandi: {ping_url}")
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(ping_url) as response:
                    logging.info(f"Ping yuborildi: {response.status}")
            except Exception as e:
                logging.error(f"Ping xatosi: {e}")
            await asyncio.sleep(600)  # 10 daqiqa

async def set_bot_description():
    """Bot kirish qismi (start bosilishidan oldin ko'rinadigan matn)ni sozlash."""
    try:
        await bot.set_my_description(
            "🍔 \"Xushmaza\" Fast Food Restoraniga Xush Kelibsiz! 🍟✨\n\n"
            "🌟 Eng mazali va sifatli taomlar, issiq va tezkor yetkazib berish!\n\n"
            "✨ Bizning bot orqali:\n"
            "• Boy va mazali menyuni ko'rish 📋\n"
            "• Qulay va tez buyurtma berish 🛒\n"
            "• Yetkazib berish va to'lov turlarini tanlash 🛵\n\n"
            "👇 Buyurtma berish uchun START tugmasini bosing!"
        )
        await bot.set_my_short_description("🍔 Xushmaza Fast Food — Mazali taomlar va tezkor yetkazib berish boti! 🍟🚀")
        logging.info("Bot ta'rifi va qisqa ma'lumoti muvaffaqiyatli o'rnatildi.")
    except Exception as e:
        logging.error(f"Bot description o'rnatishda xatolik: {e}")

async def main():
    # Keep-alive vazifasini fonda ishga tushiramiz
    asyncio.create_task(keep_alive())
    
    # Bot description va short description o'rnatish
    await set_bot_description()
    
    # Botni ishga tushirish (tarmoq uzilganda avto-qayta ulanadi)
    while True:
        try:
            logging.info("Bot polling boshlanmoqda...")
            await dp.start_polling(bot)
        except Exception as e:
            logging.error(f"Polling xatosi: {e}. 3 soniyadan so'ng qayta ulanadi...")
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())

