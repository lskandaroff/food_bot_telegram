# restaurant/serializers.py
from rest_framework import serializers
from .models import Menu, Dish

class DishSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Dish
        fields = ['id', 'title', 'price', 'description', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'title']

from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user_id', 'phone_number', 'total_products', 'total_price', 'payment_type', 'payment_receipt', 'location_latitude', 'location_longitude', 'location_text', 'created_at', 'is_active']

from .models import TelegramUser

class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ['user_id', 'first_name', 'last_name', 'username', 'phone_number']

