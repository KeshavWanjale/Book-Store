from django.contrib import admin
from .models import CartItems, CartModel


admin.site.register(CartModel)
admin.site.register(CartItems)
