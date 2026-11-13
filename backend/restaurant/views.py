# restaurant/views.py
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Menu, Dish, Order, TelegramUser
from .serializers import MenuSerializer, DishSerializer, OrderSerializer, TelegramUserSerializer

def health_check(request):
    return HttpResponse("OK")

class TelegramUserView(generics.RetrieveUpdateAPIView):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    lookup_field = 'user_id'

    def get_object(self):
        queryset = self.get_queryset()
        filter = {}
        filter[self.lookup_field] = self.kwargs[self.lookup_field]
        obj = generics.get_object_or_404(queryset, **filter)
        return obj

    def post(self, request, *args, **kwargs):
        # Create or update
        user_id = request.data.get('user_id')
        if not user_id:
             return Response({"error": "user_id is required"}, status=400)
        
        user, created = TelegramUser.objects.update_or_create(
            user_id=user_id,
            defaults=request.data
        )
        serializer = self.get_serializer(user)
        return Response(serializer.data)


import json
import requests
from django.http import HttpResponse, JsonResponse

def send_order_to_admin(order):
    """Buyurtma haqidagi ma'lumotlarni Telegram admin(lar)ga yuboradi."""
    try:
        from food_bot.config import TOKEN, ADMIN_IDS, ADMIN_ID, DELIVERY_PERSON_ID
        admin_targets = list(set(ADMIN_IDS if ADMIN_IDS else [ADMIN_ID or DELIVERY_PERSON_ID]))
        if not admin_targets:
            return

        msg_text = (
            f"🔔 <b>Yangi buyurtma! (#{order.id})</b>\n\n"
            f"📞 <b>Tel:</b> +{order.phone_number}\n"
            f"🛒 <b>Mahsulotlar:</b>\n{order.total_products}\n\n"
            f"💰 <b>Jami:</b> {order.total_price} so'm\n"
            f"💳 <b>To'lov turi:</b> {'Naqd' if order.payment_type == 'cash' else 'Karta'}\n"
        )
        if order.comment:
            msg_text += f"💬 <b>Izoh (Retsept):</b> {order.comment}\n"

        if order.location_latitude and order.location_longitude:
            maps_link = f"https://www.google.com/maps?q={order.location_latitude},{order.location_longitude}"
            msg_text += f"📍 <b>Manzil:</b> <a href='{maps_link}'>Google Maps</a>\n"
        elif order.location_text:
            msg_text += f"📍 <b>Manzil:</b> {order.location_text}\n"

        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ Qabul qilish", "callback_data": f"admin_complete_{order.id}"},
                    {"text": "❌ Bekor qilish", "callback_data": f"admin_cancel_{order.id}"}
                ]
            ]
        }

        for admin_id in admin_targets:
            if not admin_id:
                continue

        # Chek rasmi bo'lsa sendPhoto, aks holda sendMessage
            if order.payment_receipt:
                try:
                    # Supabase yoki boshqa cloud storage da URL orqali yuboramiz
                    receipt_url = order.payment_receipt.url
                    url_photo = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
                    data = {
                        'chat_id': admin_id,
                        'photo': receipt_url,
                        'caption': msg_text,
                        'parse_mode': 'HTML',
                        'reply_markup': json.dumps(inline_keyboard)
                    }
                    res = requests.post(url_photo, data=data, timeout=10)
                    print(f"Telegram sendPhoto to admin {admin_id} status: {res.status_code}")
                    if res.status_code != 200:
                        raise Exception(f"sendPhoto failed: {res.text}")
                except Exception as pe:
                    print(f"Error sending photo to admin {admin_id}: {pe}")
                    url_msg = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                    requests.post(url_msg, data={
                        "chat_id": admin_id,
                        "text": msg_text,
                        "parse_mode": "HTML",
                        "reply_markup": json.dumps(inline_keyboard)
                    }, timeout=10)
            else:
                url_msg = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                res = requests.post(url_msg, data={
                    "chat_id": admin_id,
                    "text": msg_text,
                    "parse_mode": "HTML",
                    "reply_markup": json.dumps(inline_keyboard)
                }, timeout=10)
                print(f"Telegram sendMessage to admin {admin_id} status: {res.status_code}")

            # Lokatsiya bo'lsa, xaritadagi nuqtani ham yuborish
            if order.location_latitude and order.location_longitude:
                url_loc = f"https://api.telegram.org/bot{TOKEN}/sendLocation"
                requests.post(url_loc, data={
                    "chat_id": admin_id,
                    "latitude": float(order.location_latitude),
                    "longitude": float(order.location_longitude)
                }, timeout=10)

    except Exception as e:
        print(f"Error sending order to admin: {e}")



class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        # Force is_active to True upon creation
        order = serializer.save(is_active=True)
        send_order_to_admin(order)


class MenuListView(APIView):
    def get(self, request):
        menus = Menu.objects.all()
        serializer = MenuSerializer(menus, many=True, context={'request': request})
        return Response(serializer.data)




class DishListView(APIView):
    def get(self, request, menu_id):
        dishes = Dish.objects.filter(menu_id=menu_id).order_by('order', 'id')
        serializer = DishSerializer(dishes, many=True, context={'request': request})
        return Response(serializer.data)


class DishDetailAPIView(generics.RetrieveAPIView):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer


class ActiveOrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(is_active=True).order_by('-created_at')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Order


# Attempt to import TOKEN, handle if not found or different path
try:
    from food_bot.config import TOKEN
except ImportError:
    TOKEN = 'YOUR_BOT_TOKEN_HERE' # Should be configured

@login_required
def orders_list(request):
    orders = Order.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'restaurant/orders.html', {'orders': orders})

@csrf_exempt
def complete_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=order_id)
        order.is_active = False
        order.status = 'completed'
        order.save()
        
        # Send Telegram notification to user
        try:
            from food_bot.config import TOKEN, DELIVERY_PERSON_IDS, DELIVERY_PERSON_ID
            
            # Message to customer
            user_message = f"✅ Buyurtmangiz qabul qilindi! Tayyor bo‘lsa, sizga admin xabar beradi. (Buyurtma #{order.id})"
            url_msg = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            res = requests.post(url_msg, data={"chat_id": order.user_id, "text": user_message}, timeout=10)
            print(f"Telegram sendMessage status: {res.status_code}, response: {res.text}")
            
            # Message to delivery persons
            delivery_targets = list(set(DELIVERY_PERSON_IDS if DELIVERY_PERSON_IDS else ([DELIVERY_PERSON_ID] if DELIVERY_PERSON_ID else [])))
            for dev_id in delivery_targets:
                if not dev_id:
                    continue
                delivery_message = (
                    f"🚚 <b>Yangi yetkazib berish!</b>\n\n"
                    f"🔢 Buyurtma: #{order.id}\n"
                    f"📞 Tel: +{order.phone_number}\n"
                    f"🍔 Mahsulotlar:\n{order.total_products}\n"
                    f"💰 Jami: {order.total_price} so'm\n"
                )
                if order.comment:
                    delivery_message += f"💬 Izoh: {order.comment}\n"
                
                if order.location_latitude and order.location_longitude:
                    maps_link = f"https://www.google.com/maps?q={order.location_latitude},{order.location_longitude}"
                    delivery_message += f"\n📍 Manzil: <a href='{maps_link}'>Google Maps</a>"
                    
                    requests.post(url_msg, data={
                        "chat_id": dev_id,
                        "text": delivery_message,
                        "parse_mode": "HTML"
                    }, timeout=10)
                    
                    url_loc = f"https://api.telegram.org/bot{TOKEN}/sendLocation"
                    requests.post(url_loc, data={
                        "chat_id": dev_id,
                        "latitude": float(order.location_latitude),
                        "longitude": float(order.location_longitude)
                    }, timeout=10)
                elif order.location_text:
                    delivery_message += f"\n📍 Manzil: {order.location_text}"
                    requests.post(url_msg, data={
                        "chat_id": dev_id,
                        "text": delivery_message,
                        "parse_mode": "HTML"
                    }, timeout=10)
        except Exception as e:
            print(f"Error sending telegram message: {e}")

            
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'order_id': order.id})
        return redirect('orders_list')
    return redirect('orders_list')

@csrf_exempt
def cancel_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=order_id)
        order.is_active = False
        order.status = 'cancelled'
        order.save()
        
        # Send Telegram notification
        try:
            from food_bot.config import TOKEN
            message = f"❌ Buyurtmangiz bekor qilindi. (Buyurtma #{order.id})\nAgar savollaringiz bo'lsa, admin bilan bog'laning."
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            data = {
                "chat_id": order.user_id,
                "text": message
            }
            res = requests.post(url, data=data, timeout=10)
            print(f"Telegram cancel_order status: {res.status_code}, response: {res.text}")
        except Exception as e:
            print(f"Error sending telegram message: {e}")
            
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'order_id': order.id})
        return redirect('orders_list')
    return redirect('orders_list')




@login_required
def orders_history(request):
    orders = Order.objects.filter(is_active=False).order_by('-created_at')
    return render(request, 'restaurant/history.html', {'orders': orders})

from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.cache import never_cache

@xframe_options_exempt
@never_cache
def webapp_menu(request):
    response = render(request, 'restaurant/webapp.html')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


import traceback as tb_module
from django.http import JsonResponse

def debug_dish(request, dish_id):
    """
    Vaqtinchalik debug endpoint — /debug/dish/<id>/
    Dish ma'lumotlari va storage holatini tekshiradi.
    Muammo topilgandan keyin bu viewni o'chirish kerak.
    """
    result = {}

    # 1. Storage tekshiruv
    try:
        from restaurant.supabase_storage import SupabaseStorage
        s = SupabaseStorage()
        result['storage'] = {
            'supabase_url': s.supabase_url,
            'bucket': s.bucket,
            'key_length': len(s.supabase_key),
            'key_start': s.supabase_key[:20] + '...',
        }
    except Exception as e:
        result['storage_error'] = str(e)
        result['storage_traceback'] = tb_module.format_exc()

    # 2. Dish tekshiruv
    try:
        from restaurant.models import Dish
        dish = Dish.objects.get(id=dish_id)
        result['dish'] = {
            'id': dish.id,
            'title': dish.title,
            'image_name': repr(dish.image.name),
            'image_name_bool': bool(dish.image.name),
        }
    except Dish.DoesNotExist:
        result['dish_error'] = f'Dish id={dish_id} topilmadi'
        return JsonResponse(result, status=404)
    except Exception as e:
        result['dish_error'] = str(e)
        result['dish_traceback'] = tb_module.format_exc()
        return JsonResponse(result, status=500)

    # 3. Image URL tekshiruv
    try:
        if dish.image and dish.image.name:
            url = dish.image.url
            result['dish']['image_url'] = url
        else:
            result['dish']['image_url'] = None
            result['dish']['image_warning'] = 'Image name bosh yoki None'
    except Exception as e:
        result['image_url_error'] = str(e)
        result['image_url_traceback'] = tb_module.format_exc()

    # 4. Supabase ulanish tekshiruvi
    try:
        import requests as req
        resp = req.get(
            f"{s.supabase_url}/storage/v1/bucket/{s.bucket}",
            headers={'apikey': s.supabase_key, 'Authorization': f'Bearer {s.supabase_key}'},
            timeout=8
        )
        result['supabase_connection'] = {
            'status': resp.status_code,
            'response': resp.text[:300],
        }
    except Exception as e:
        result['supabase_connection_error'] = str(e)

    result['status'] = 'OK'
    return JsonResponse(result, json_dumps_params={'indent': 2})

