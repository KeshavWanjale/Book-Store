from .views import CartsViews, CartsViewsByID, OrderViews, OrderViewsByID
from django.urls import path

urlpatterns = [
    path('',CartsViews.as_view(),name='cart-list'),
    path('<int:pk>',CartsViewsByID.as_view(),name='cart-details'),
    path('orders',OrderViews.as_view(),name='order-list'),
    path('orders/<int:pk>',OrderViewsByID.as_view(),name='order-details'),
]
