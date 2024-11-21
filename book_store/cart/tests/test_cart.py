import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from book.models import Book
from cart.models import CartModel, CartItems

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_user(api_client):
    user = User.objects.create_user(username="UserOne",email="testuser@example.com", password="testpassword")
    api_client.force_authenticate(user=user)
    return user

@pytest.fixture
def book(authenticated_user):
    return Book.objects.create(name="Test Book", author="Author Name", stock=10, price=100,user_id=authenticated_user.id)

@pytest.fixture
def active_cart(authenticated_user):
    return CartModel.objects.create(user=authenticated_user, is_ordered=False)

# Cart Test Cases
@pytest.mark.django_db
def test_get_active_cart(api_client, authenticated_user, active_cart):
    url = reverse('cart-list')
    response = api_client.get(url) 
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "success"

@pytest.mark.django_db
def test_get_no_active_cart(api_client, authenticated_user):
    url = reverse('cart-list')
    response = api_client.get(url) 
    assert response.status_code == 404
    assert response.data["status"] == "error"

@pytest.mark.django_db
def test_get_cart_unauth(api_client):
    url = reverse('cart-list')
    response = api_client.get(url) 
    assert response.status_code == 401

@pytest.mark.django_db
def test_get_active_cart_no_cart(api_client, authenticated_user):
    url = reverse('cart-list')
    response = api_client.get(url) 
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["message"] == "No active cart found for the user"

@pytest.mark.django_db
def test_post_add_to_cart(api_client, authenticated_user, book):
    payload = {
        "book_id": book.id,
        "quantity": 2
    }
    url = reverse('cart-list')
    response = api_client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == "success"
    assert response.data["cart"]["total_quantity"] == 2
    assert response.data["cart"]["total_price"] == 200

@pytest.mark.django_db
def test_post_add_to_cart_insufficient_stock(api_client, authenticated_user, book):
    payload = {
        "book_id": book.id,
        "quantity": 20
    }
    url = reverse('cart-list')
    response = api_client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["message"] == "Insufficient stock. Only 10 available."


# Order Test Cases
@pytest.mark.django_db
def test_get_orders(api_client, authenticated_user):
    url = reverse('order-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["message"] == "No order Found"

@pytest.mark.django_db
def test_post_place_order(api_client, authenticated_user, active_cart, book):
    CartItems.objects.create(cart=active_cart, book=book, quantity=2, price=200)
    url = reverse('order-list')
    response = api_client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "The order placed"
    book.refresh_from_db()
    assert book.stock == 8

@pytest.mark.django_db
def test_post_place_order_no_cart(api_client, authenticated_user):
    url = reverse('order-list')
    response = api_client.post(url)
    assert response.status_code == 400
