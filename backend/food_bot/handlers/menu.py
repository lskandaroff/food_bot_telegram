from aiogram import Router, types, F
from aiogram.types import CallbackQuery, FSInputFile
import aiohttp
import logging
from urllib.parse import unquote
from pathlib import Path
from config import API_URL, LOCAL_API_URL
from keyboards import get_dishes_keyboard, get_dish_detail_keyboard, get_menus_keyboard

router = Router()

@router.message(F.text == "🍽 Menular")
async def show_menu(message: types.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{LOCAL_API_URL}/api/menus/") as response:
                if response.status == 200:
                    menus = await response.json()
                    if menus:
                        await message.answer("🍽 Menuni tanlang:", reply_markup=get_menus_keyboard(menus))
                    else:
                        await message.answer("Hozircha bo'limlar yaratilmagan. Iltimos, keyinroq qayta urunib ko'ring.")
                else:
                    await message.answer("Xatolik: Menu ma'lumotlarini yuklab bo'lmadi.")
    except Exception:
        await message.answer("Serverga ulanishda xatolik yuz berdi.")

@router.message(F.text == "⬅️ Ortga")
async def back_to_main_text(message: types.Message):
    from keyboards import get_main_keyboard
    await message.answer("Asosiy menu:", reply_markup=get_main_keyboard())

@router.callback_query(F.data.startswith("menu_"))
async def menu_selected(callback: CallbackQuery):
    menu_id = callback.data.split("_")[1]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{LOCAL_API_URL}/api/menus/{menu_id}/dishes/") as resp:
            if resp.status != 200:
                await callback.message.answer("Taomlar topilmadi!")
                return
            dishes = await resp.json()

    await callback.message.answer("🍲 Taomni tanlang:", reply_markup=get_dishes_keyboard(dishes))

@router.callback_query(F.data.startswith("dish_"))
async def dish_selected(callback: CallbackQuery):
    dish_id = callback.data.split("_")[1]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{LOCAL_API_URL}/api/dishes/{dish_id}/") as resp:
            if resp.status != 200:
                await callback.message.answer("Taom topilmadi!")
                return
            dish = await resp.json()

    # Rasm nomini olish
    image_url = dish.get('image')
    photo_input = None

    if image_url:
        if "/media/" in image_url:
            relative_path = unquote(image_url.split("/media/")[-1])
            # Baza yo'lini aniqlash (backend/media)
            base_dir = Path(__file__).resolve().parent.parent.parent
            local_image_path = base_dir / "media" / relative_path

            if local_image_path.exists():
                photo_input = FSInputFile(local_image_path)
            elif image_url.startswith("http"):
                # Agar localda bo'lmasa, URL orqali yuboramiz
                photo_input = image_url
        elif image_url.startswith("http"):
            photo_input = image_url

    text = f"🍽 {dish['title']}\n" \
           f"💰 Narxi: {dish['price']}\n" \
           f"📝 Tavsifi: {dish.get('description', 'Yo‘q')}"

    if photo_input:
        try:
            await callback.message.answer_photo(
                photo=photo_input, 
                caption=text, 
                reply_markup=get_dish_detail_keyboard(dish['id'])
            )
        except Exception as e:
            logging.error(f"Rasm yuborishda xato: {e}")
            await callback.message.answer(text, reply_markup=get_dish_detail_keyboard(dish['id']))
    else:
        await callback.message.answer(text, reply_markup=get_dish_detail_keyboard(dish['id']))

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{LOCAL_API_URL}/api/menus/") as response:
            menus = await response.json()
    
    await callback.message.delete()
    await callback.message.answer("🍽 Menuni tanlang:", reply_markup=get_menus_keyboard(menus))

import json
from aiogram.fsm.context import FSMContext
from states import OrderFood
from keyboards import get_location_keyboard, get_contact_keyboard

@router.message(F.web_app_data)
async def handle_web_app_data(message: types.Message, state: FSMContext):
    data = message.web_app_data.data
    try:
        parsed_data = json.loads(data)
        if parsed_data.get('action') == 'checkout':
            items = parsed_data.get('items', [])
            cart = []
            for item in items:
                # Web app sends items with quantity, we add them to cart
                # To match existing cart format, we can add it multiple times or just store it.
                # The existing cart expects list of items: {'id': 1, 'title': '...', 'price': 100}
                # So we expand the quantity back to list
                for _ in range(item['quantity']):
                    cart.append({
                        "id": item['id'],
                        "title": item['title'],
                        "price": float(item['price'])
                    })
            
            await state.update_data(cart=cart)
            
            # Show cart instead of proceeding to checkout immediately
            from handlers.cart import _show_cart_logic
            await _show_cart_logic(message, state, is_callback=False)

    except json.JSONDecodeError:
        await message.answer("Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")
