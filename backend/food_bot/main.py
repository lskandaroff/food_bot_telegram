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

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
