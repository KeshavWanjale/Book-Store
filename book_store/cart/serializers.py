from rest_framework import serializers
from .models import CartModel, CartItems
from book.models import Book

class CartItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CartItems
        fields = ['id', 'book', 'quantity', 'price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = CartModel
        fields = ['id', 'user', 'total_price', 'total_quantity', 'is_ordered', 'items']
        read_only_fields = ['total_price', 'total_quantity', 'is_ordered']
