from aiogram import Router, types
from aiogram.filters import Command
import aiohttp
from config import API_URL
from keyboards import get_menus_keyboard, get_main_keyboard

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Xush kelibsiz! 🍲", reply_markup=get_main_keyboard())
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/menus/") as response:
            menus = await response.json()

    await message.answer("🍽 Menuni tanlang:", reply_markup=get_menus_keyboard(menus))
