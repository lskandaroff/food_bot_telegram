from aiogram import Router, types
from aiogram.filters import Command
import aiohttp
from config import API_URL
from keyboards import get_menus_keyboard, get_main_keyboard

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Xush kelibsiz! 🍲", reply_markup=get_main_keyboard())
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/api/menus/") as response:
                if response.status == 200:
                    menus = await response.json()
                    if menus:
                        await message.answer("🍽 Menuni tanlang:", reply_markup=get_menus_keyboard(menus))
                    else:
                        await message.answer("Hozircha bo'limlar yaratilmagan. Iltimos, keyinroq qayta urunib ko'ring.")
                else:
                    await message.answer("Xatolik: Menu ma'lumotlarini yuklab bo'lmadi.")
    except Exception:
        await message.answer("Serverga ulanishda xatolik yuz berdi. Iltimos, admin panelda bo'limlar borligini tekshiring.")
