from aiogram import Router, F
from aiogram.types import CallbackQuery
import aiohttp
from config import LOCAL_API_URL

router = Router()

@router.callback_query(F.data.startswith("admin_complete_"))
async def admin_complete_order(callback: CallbackQuery):
    order_id = callback.data.split("_")[2]
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{LOCAL_API_URL}/api/orders/{order_id}/complete/") as resp:
                if resp.status in [200, 302]:
                    await callback.answer(f"✅ Buyurtma #{order_id} tayyorlandi!", show_alert=True)
                    
                    status_text = "\n\n✅ <b>HOLAT: Tayyorlandi</b>"
                    if callback.message.caption:
                        new_caption = callback.message.caption + status_text
                        await callback.message.edit_caption(caption=new_caption, parse_mode="HTML", reply_markup=None)
                    elif callback.message.text:
                        new_text = callback.message.text + status_text
                        await callback.message.edit_text(text=new_text, parse_mode="HTML", reply_markup=None)
                else:
                    await callback.answer(f"❌ Xatolik yuz berdi! (Status: {resp.status})", show_alert=True)
        except Exception as e:
            await callback.answer(f"❌ Ulanishda xatolik: {e}", show_alert=True)


@router.callback_query(F.data.startswith("admin_cancel_"))
async def admin_cancel_order(callback: CallbackQuery):
    order_id = callback.data.split("_")[2]
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{LOCAL_API_URL}/api/orders/{order_id}/cancel/") as resp:
                if resp.status in [200, 302]:
                    await callback.answer(f"❌ Buyurtma #{order_id} bekor qilindi!", show_alert=True)
                    
                    status_text = "\n\n❌ <b>HOLAT: Bekor qilindi</b>"
                    if callback.message.caption:
                        new_caption = callback.message.caption + status_text
                        await callback.message.edit_caption(caption=new_caption, parse_mode="HTML", reply_markup=None)
                    elif callback.message.text:
                        new_text = callback.message.text + status_text
                        await callback.message.edit_text(text=new_text, parse_mode="HTML", reply_markup=None)
                else:
                    await callback.answer(f"❌ Xatolik yuz berdi! (Status: {resp.status})", show_alert=True)
        except Exception as e:
            await callback.answer(f"❌ Ulanishda xatolik: {e}", show_alert=True)
