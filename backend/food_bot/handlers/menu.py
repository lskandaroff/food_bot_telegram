from aiogram import Router, types, F
from aiogram.types import CallbackQuery, FSInputFile
import aiohttp
from urllib.parse import unquote
from pathlib import Path
from config import API_URL
from keyboards import get_dishes_keyboard, get_dish_detail_keyboard, get_menus_keyboard

router = Router()

@router.message(F.text == "📋 Menu")
async def show_menu(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/menus/") as response:
            menus = await response.json()
    
    await message.answer("🍽 Menuni tanlang:", reply_markup=get_menus_keyboard(menus))

@router.callback_query(F.data.startswith("menu_"))
async def menu_selected(callback: CallbackQuery):
    menu_id = callback.data.split("_")[1]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/menus/{menu_id}/dishes/") as resp:
            if resp.status != 200:
                await callback.message.answer("Taomlar topilmadi!")
                return
            dishes = await resp.json()

    await callback.message.answer("🍲 Taomni tanlang:", reply_markup=get_dishes_keyboard(dishes))

@router.callback_query(F.data.startswith("dish_"))
async def dish_selected(callback: CallbackQuery):
    dish_id = callback.data.split("_")[1]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/dishes/{dish_id}/") as resp:
            if resp.status != 200:
                await callback.message.answer("Taom topilmadi!")
                return
            dish = await resp.json()

    # Rasm nomini olish
    image_url = dish.get('image')
    photo_file = None

    if image_url:
        print(f"DEBUG: Processing image_url: {image_url}")
        if "/media/" in image_url:
            relative_path = unquote(image_url.split("/media/")[-1])
            print(f"DEBUG: Decoded relative_path: {relative_path}")
            # Local media path calculation
            base_dir = Path(__file__).resolve().parent.parent.parent
            local_image_path = base_dir / "media" / relative_path
            print(f"DEBUG: Local image path: {local_image_path}")
            print(f"DEBUG: Path exists: {local_image_path.exists()}")

            if local_image_path.exists():
                photo_file = FSInputFile(local_image_path)

    text = f"🍽 {dish['title']}\n" \
           f"💰 Narxi: {dish['price']}\n" \
           f"📝 Tavsifi: {dish.get('description', 'Yo‘q')}\n" \
           f"📦 Ingredientlar: {', '.join(dish.get('ingredients', []))}"

    if photo_file:
        await callback.message.answer_photo(photo=photo_file, caption=text, reply_markup=get_dish_detail_keyboard(dish['id']))
    else:
        await callback.message.answer(text, reply_markup=get_dish_detail_keyboard(dish['id']))

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/menus/") as response:
            menus = await response.json()
    
    await callback.message.delete()
    await callback.message.answer("🍽 Menuni tanlang:", reply_markup=get_menus_keyboard(menus))
