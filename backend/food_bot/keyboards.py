from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def get_menus_keyboard(menus):
    keyboard = InlineKeyboardBuilder()
    for m in menus:
        keyboard.button(text=m['title'], callback_data=f"menu_{m['id']}")
    
    keyboard.button(text="🛒 Savat", callback_data="cart_show")
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_dishes_keyboard(dishes):
    keyboard = InlineKeyboardBuilder()
    for d in dishes:
        keyboard.button(text=d['title'], callback_data=f"dish_{d['id']}")
    
    keyboard.button(text="🛒 Savat", callback_data="cart_show")
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_dish_detail_keyboard(dish_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🛒 Savatga qo'shish", callback_data=f"cart_add_{dish_id}")
    keyboard.button(text="🛒 Savat", callback_data="cart_show")
    keyboard.button(text="⬅️ Menuga qaytish", callback_data="back_to_menu")
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_cart_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Buyurtma berish", callback_data="order_confirm")
    keyboard.button(text="🗑 Savatni tozalash", callback_data="cart_clear")
    keyboard.button(text="⬅️ Menuga qaytish", callback_data="back_to_menu")
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_contact_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="📞 Telefon raqamni yuborish", request_contact=True)
    return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_location_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="📍 Lokatsiyani yuborish", request_location=True)
    return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)

from config import API_URL
from aiogram.types import WebAppInfo

def get_main_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="📋 Menu", web_app=WebAppInfo(url=f"{API_URL}/api/webapp/"))
    return keyboard.as_markup(resize_keyboard=True)

def get_payment_type_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="💵 Naqd")
    keyboard.button(text="💳 Karta")
    return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)
