from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import aiohttp
from config import API_URL, LOCAL_API_URL
from keyboards import get_cart_keyboard, get_contact_keyboard, get_location_keyboard, get_payment_type_keyboard
from states import OrderFood

router = Router()

@router.callback_query(F.data.startswith("cart_add_"))
async def add_to_cart(callback: CallbackQuery, state: FSMContext):
    dish_id = callback.data.split("_")[2]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{LOCAL_API_URL}/api/dishes/{dish_id}/") as resp:
            if resp.status == 200:
                dish = await resp.json()
                
                user_data = await state.get_data()
                cart = user_data.get("cart", [])
                cart.append({
                    "id": dish['id'],
                    "title": dish['title'],
                    "price": dish['price']
                })
                await state.update_data(cart=cart)
                
                await callback.answer(f"✅ {dish['title']} savatga qo'shildi!")
            else:
                await callback.answer("Xatolik bo'ldi!")

@router.callback_query(F.data == "cart_show")
async def show_cart(callback: CallbackQuery, state: FSMContext):
    await _show_cart_logic(callback.message, state, is_callback=True, callback_query=callback)

@router.message(F.text == "🛒 Savat")
async def show_cart_text(message: Message, state: FSMContext):
    await _show_cart_logic(message, state, is_callback=False)

async def _show_cart_logic(message: Message, state: FSMContext, is_callback=False, callback_query=None):
    user_data = await state.get_data()
    cart = user_data.get("cart", [])

    if not cart:
        if is_callback and callback_query:
            await callback_query.answer("Savatingiz bo'sh!", show_alert=True)
        else:
            await message.answer("Savatingiz bo'sh!")
        return

    text = "🛒 <b>Savatdagi mahsulotlar:</b>\n\n"
    total_price = 0
    for item in cart:
        text += f"▪️ {item['title']} - {item['price']} so'm\n"
        total_price += item['price']
    
    text += f"\n<b>Jami: {total_price} so'm</b>"

    await message.answer(text, reply_markup=get_cart_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "cart_clear")
async def clear_cart(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cart=[])
    await callback.message.edit_text("🗑 Savat tozalandi!")

@router.callback_query(F.data == "order_confirm")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    # Check if user exists
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{LOCAL_API_URL}/api/users/{user_id}/") as resp:
            if resp.status == 200:
                user_data = await resp.json()
                if user_data.get('phone_number'):
                    # Phone number exists, skip asking
                    await state.update_data(phone=user_data['phone_number'])
                    await callback.message.answer("📍 Iltimos, joylashuvingizni yuboring:", reply_markup=get_location_keyboard())
                    await state.set_state(OrderFood.WaitingForLocation)
                    await callback.answer()
                    return

    await callback.message.answer("📞 Iltimos, telefon raqamingizni yuboring:", reply_markup=get_contact_keyboard())
    await state.set_state(OrderFood.WaitingForPhone)
    await callback.answer()

@router.message(OrderFood.WaitingForPhone)
async def process_phone(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    # Save user phone to backend
    user_data = {
        "user_id": message.from_user.id,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
        "username": message.from_user.username,
        "phone_number": phone
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{LOCAL_API_URL}/api/users/create/", json=user_data) as resp:
            if resp.status not in [200, 201]:
                print(f"Failed to save user: {await resp.text()}")

    await state.update_data(phone=phone)
    await message.answer("📍 Iltimos, joylashuvingizni yuboring:", reply_markup=get_location_keyboard())
    await state.set_state(OrderFood.WaitingForLocation)

@router.message(OrderFood.WaitingForLocation)
async def process_location(message: Message, state: FSMContext):
    if message.location:
        location = f"{message.location.latitude}, {message.location.longitude}"
        await state.update_data(location=location)
        await message.answer("💰 To'lov turini tanlang:", reply_markup=get_payment_type_keyboard())
        await state.set_state(OrderFood.ChoosingPaymentType)
    else:
        # User sent text or something other than location
        await message.answer(
            "❌ Iltimos, lokatsiyangizni yuboring!\n\n"
            "📍 Pastdagi '📍 Lokatsiyani yuborish' tugmasini bosing.",
            reply_markup=get_location_keyboard()
        )


@router.message(OrderFood.ChoosingPaymentType)
async def process_payment_type(message: Message, state: FSMContext):
    payment_type = message.text
    
    if payment_type == "💵 Naqd":
        await create_order(message, state, "cash")
    elif payment_type == "💳 Karta":
        await message.answer(
            "💳 <b>Click orqali to'lov:</b>\n\n"
            "📞 <b>+998 90 123 45 67</b> (Ali V.)\n\n"
            "Iltimos, to'lovni amalga oshirib, chek rasmini yuboring (vaqti ham ko'rinsin).",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(OrderFood.WaitingForReceipt)
    else:
        await message.answer("Iltimos, to'lov turini tugmalar orqali tanlang.")

@router.message(OrderFood.WaitingForReceipt, F.photo)
async def process_receipt(message: Message, state: FSMContext):
    photo = message.photo[-1]
    
    file_id = photo.file_id
    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    
    import os
    if not os.path.exists("temp"):
        os.makedirs("temp")
    
    temp_filename = f"temp/{file_id}.jpg"
    await message.bot.download_file(file_path, temp_filename)
    
    await create_order(message, state, "card", receipt_path=temp_filename)
    
    if os.path.exists(temp_filename):
        os.remove(temp_filename)

async def create_order(message: Message, state: FSMContext, payment_type: str, receipt_path: str = None):
    user_data = await state.get_data()
    cart = user_data.get("cart", [])
    phone = user_data.get("phone")
    location = user_data.get("location")
    
    total_price = sum(item['price'] for item in cart)
    
    from collections import Counter
    product_counts = Counter(item['title'] for item in cart)
    products_summary = ", ".join([f"{title} {count} ta" for title, count in product_counts.items()])
    
    data = aiohttp.FormData()
    data.add_field('user_id', str(message.from_user.id))
    data.add_field('phone_number', phone)
    data.add_field('total_products', products_summary)
    data.add_field('total_price', str(total_price))
    data.add_field('payment_type', payment_type)
    
    if location:
        try:
            lat, lon = location.split(", ")
            data.add_field('location_latitude', lat)
            data.add_field('location_longitude', lon)
        except ValueError:
            data.add_field('location_text', location)
    
    if receipt_path:
        data.add_field('payment_receipt',
                       open(receipt_path, 'rb'),
                       filename='receipt.jpg',
                       content_type='image/jpeg')

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{LOCAL_API_URL}/api/orders/create/", data=data) as resp:
                if resp.status == 201:
                    print(f"Order saved: {await resp.json()}")
                else:
                    print(f"Failed to save order: {await resp.text()}")
        except Exception as e:
            print(f"Error saving order: {e}")

    summary = "✅ Buyurtma qabul qilindi!\n\n"
    summary += f"📞 Telefon: {phone}\n"
    summary += f"📍 Manzil: {location}\n"
    summary += f"💰 To'lov turi: {'Naqd' if payment_type == 'cash' else 'Karta'}\n"
    summary += f"💰 Jami: {total_price} so'm"
    summary += "\n\nTez orada operatorimiz siz bilan bog'lanadi."

    from keyboards import get_main_keyboard
    await message.answer(summary, reply_markup=get_main_keyboard())
    await state.clear()
