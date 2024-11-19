from django.db import models
from django.conf import settings
from book.models import Book


class CartModel(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price=models.PositiveBigIntegerField(default=0)
    total_quantity=models.PositiveBigIntegerField(default=0)
    is_ordered=models.BooleanField(default=False)


class CartItems(models.Model):
    cart = models.ForeignKey(CartModel, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0) 
