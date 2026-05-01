from django.urls import path
from .views import DishListView, MenuListView, DishDetailAPIView, orders_list, complete_order, cancel_order, OrderCreateView, orders_history, ActiveOrderListAPIView, TelegramUserView, webapp_menu

urlpatterns = [
    path('menus/', MenuListView.as_view()),
    path('menus/<int:menu_id>/dishes/', DishListView.as_view()),
    path('dishes/<int:pk>/', DishDetailAPIView.as_view(), name='dish-detail'),
    path('orders/', orders_list, name='orders_list'),
    path('orders/history/', orders_history, name='orders_history'),
    path('orders/<int:order_id>/complete/', complete_order, name='complete_order'),
    path('orders/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
    path('orders/create/', OrderCreateView.as_view(), name='api_order_create'),
    path('active-orders/', ActiveOrderListAPIView.as_view(), name='api_active_orders'),
    path('users/<int:user_id>/', TelegramUserView.as_view(), name='api_user_detail'),
    path('users/create/', TelegramUserView.as_view(), name='api_user_create'),
    path('webapp/', webapp_menu, name='webapp_menu'),
]
