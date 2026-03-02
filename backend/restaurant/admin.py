from django.contrib import admin
from .models import Dish, Menu, Order, TelegramUser

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'menu', 'price')
    list_filter = ('menu',)
    search_fields = ('title',)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'phone_number', 'total_price', 'status', 'is_active', 'created_at')
    list_filter = ('status', 'is_active', 'payment_type', 'created_at')
    search_fields = ('phone_number', 'user_id', 'total_products')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    actions = ['clear_history']

    @admin.action(description="Tarixni tozalash (faol bo'lmagan buyurtmalarni o'chirish)")
    def clear_history(self, request, queryset):
        deleted, _ = Order.objects.filter(is_active=False).delete()
        self.message_user(request, f"{deleted} ta tarixiy buyurtma o'chirildi.")

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_name', 'last_name', 'username', 'phone_number', 'created_at')
    search_fields = ('user_id', 'first_name', 'last_name', 'username', 'phone_number')
    readonly_fields = ('created_at',)

