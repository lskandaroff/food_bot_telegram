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


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        # Force is_active to True upon creation
        serializer.save(is_active=True)


class MenuListView(APIView):
    def get(self, request):
        menus = Menu.objects.all()
        serializer = MenuSerializer(menus, many=True, context={'request': request})
        return Response(serializer.data)




class DishListView(APIView):
    def get(self, request, menu_id):
        dishes = Dish.objects.filter(menu_id=menu_id)
        serializer = DishSerializer(dishes, many=True)
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
from .models import Order
import requests


# Attempt to import TOKEN, handle if not found or different path
try:
    from food_bot.config import TOKEN
except ImportError:
    TOKEN = 'YOUR_BOT_TOKEN_HERE' # Should be configured

@login_required
def orders_list(request):
    orders = Order.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'restaurant/orders.html', {'orders': orders})

@login_required
def complete_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=order_id)
        order.is_active = False
        order.status = 'completed'
        order.save()
        
        # Send Telegram notification to user
        try:
            from food_bot.config import DELIVERY_PERSON_ID
            
            # Message to customer
            user_message = f"✅ Buyurtmangiz tayyor bo‘ldi! (Buyurtma #{order.id})"
            url_msg = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(url_msg, data={"chat_id": order.user_id, "text": user_message})
            
            # Message to delivery person
            if DELIVERY_PERSON_ID:
                delivery_message = (
                    f"🚚 <b>Yangi yetkazib berish!</b>\n\n"
                    f"🔢 Buyurtma: #{order.id}\n"
                    f"📞 Tel: +{order.phone_number}\n"
                    f"🍔 Mahsulotlar: {order.total_products}\n"
                    f"💰 Jami: {order.total_price} so'm\n"
                )
                
                if order.location_latitude and order.location_longitude:
                    # Send Google Maps link
                    maps_link = f"https://www.google.com/maps?q={order.location_latitude},{order.location_longitude}"
                    delivery_message += f"\n📍 Manzil: <a href='{maps_link}'>Google Maps</a>"
                    
                    # Send message with link
                    requests.post(url_msg, data={
                        "chat_id": DELIVERY_PERSON_ID,
                        "text": delivery_message,
                        "parse_mode": "HTML"
                    })
                    
                    # Also send actual Telegram location message
                    url_loc = f"https://api.telegram.org/bot{TOKEN}/sendLocation"
                    requests.post(url_loc, data={
                        "chat_id": DELIVERY_PERSON_ID,
                        "latitude": order.location_latitude,
                        "longitude": order.location_longitude
                    })
                elif order.location_text:
                    delivery_message += f"\n📍 Manzil: {order.location_text}"
                    requests.post(url_msg, data={
                        "chat_id": DELIVERY_PERSON_ID,
                        "text": delivery_message,
                        "parse_mode": "HTML"
                    })
        except Exception as e:
            print(f"Error sending telegram message: {e}")
            
        return redirect('orders_list')
    return redirect('orders_list')

@login_required
def cancel_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=order_id)
        order.is_active = False
        order.status = 'cancelled'
        order.save()
        
        # Send Telegram notification
        try:
            message = f"❌ Buyurtmangiz bekor qilindi. (Buyurtma #{order.id})\nAgar savollaringiz bo'lsa, admin bilan bog'laning."
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            data = {
                "chat_id": order.user_id,
                "text": message
            }
            requests.post(url, data=data)
        except Exception as e:
            print(f"Error sending telegram message: {e}")
            
        return redirect('orders_list')
    return redirect('orders_list')


@login_required
def orders_history(request):
    orders = Order.objects.filter(is_active=False).order_by('-created_at')
    return render(request, 'restaurant/history.html', {'orders': orders})

def webapp_menu(request):
    return render(request, 'restaurant/webapp.html')
