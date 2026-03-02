from django.db import models
# restaurant/models.py

class Menu(models.Model):
    title = models.CharField(max_length=100)
    # image = models.ImageField(upload_to='menus/')
    # narxni olib tashlaymiz
    # price = models.IntegerField()  # kerak emas

    def __str__(self):
        return self.title

class Dish(models.Model):
    menu = models.ForeignKey(Menu, related_name='dishes', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField(blank=True)  # tarkibi

    image = models.ImageField(upload_to='dishes/')

    def __str__(self):
        return self.title

class Order(models.Model):
    user_id = models.BigIntegerField()
    phone_number = models.CharField(max_length=20)
    total_products = models.TextField()
    total_price = models.IntegerField()
    PAYMENT_TYPES = (
        ('cash', 'Naqd'),
        ('card', 'Karta'),
    )
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('completed', 'Tayyorlandi'),
        ('cancelled', 'Bekor qilindi'),
    )
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES, default='cash')
    payment_receipt = models.ImageField(upload_to='receipts/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_text = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Order {self.id} - {self.phone_number}"

class TelegramUser(models.Model):
    user_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} ({self.user_id})"
