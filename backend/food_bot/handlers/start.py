from aiogram import Router, types
from aiogram.filters import Command
import aiohttp
from config import API_URL, LOCAL_API_URL
from keyboards import get_menus_keyboard, get_main_keyboard

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    welcome_text = (
        f"👋 <b>Assalomu aleykum, {message.from_user.first_name}!</b>\n\n"
        "🍔 <b>\"Xushmaza\" Fast Food</b> restoraniga xush kelibsiz! 🍟✨\n\n"
        "Eng mazali va sifatli fast-food taomlarini tezkor yetkazib beramiz! 🚀\n\n"
        "Quyidagi tugmalardan birini tanlang:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

