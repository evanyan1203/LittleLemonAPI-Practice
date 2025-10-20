from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework.authtoken.models import Token


admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)