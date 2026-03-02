from aiogram import Bot, Dispatcher
import asyncio
import logging
from config import TOKEN
from handlers import start, menu, cart

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

async def main():
    # Keep-alive vazifasini fonda ishga tushiramiz
    asyncio.create_task(keep_alive())
    
    # Botni ishga tushirish
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
