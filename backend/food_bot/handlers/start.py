from aiogram import Router, types
from aiogram.filters import Command
import aiohttp
from config import API_URL
from keyboards import get_menus_keyboard, get_main_keyboard

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Xush kelibsiz! 🍲\n\nQuyidagi tugmalardan birini tanlang:", reply_markup=get_main_keyboard())
