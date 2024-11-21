import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from book.models import Book
from user.models import CustomUser

@pytest.fixture
def api_client():
    """Returns an instance of the API client."""
    return APIClient()

@pytest.fixture
def superuser():
    """Creates and returns a superuser."""
    return CustomUser.objects.create_superuser(
        username="Admin",
        email="admin@example.com",
        password="Superpassword@123"
    )

@pytest.fixture
def regular_user():
    """Creates and returns a regular user."""
    return CustomUser.objects.create_user(
        username="user",
        email="user@example.com",
        password="userpassword"
    )

@pytest.fixture
def book(superuser):
    """Creates and returns a book instance."""
    return Book.objects.create(
        name="Test Book",
        author="Author Name",
        price=100,
        stock=10,
        user=superuser
    )

@pytest.mark.django_db
def test_list_books(api_client, regular_user):
    """Test listing books."""
    token = RefreshToken.for_user(regular_user).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # Test listing books
    url = reverse('books-list')  
    response = api_client.get(url)

    assert response.status_code == 200
    assert isinstance(response.data, list)

@pytest.mark.django_db
def test_list_books_unauth(api_client, regular_user):
    """Test listing books."""
    token = "RefreshToken.for_user(regular_user).access_token"
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    url = reverse('books-list')  
    response = api_client.get(url)

    assert response.status_code == 401

@pytest.mark.django_db
def test_create_book_as_superuser(api_client, superuser):
    """Test creating a book as a superuser."""
    token = RefreshToken.for_user(superuser).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    url = reverse('books-list')
    payload = {
        "name": "New Book",
        "author": "New Author",
        "price": 150,
        "stock": 5
    }
    response = api_client.post(url, payload)

    assert response.status_code == 201
    assert response.data['message'] == "Book created successfully"
    assert response.data['data']['name'] == "New Book"

@pytest.mark.django_db
def test_create_book_as_regular_user(api_client, regular_user):
    """Test creating a book as a regular user."""
    token = RefreshToken.for_user(regular_user).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    url = reverse('books-list')  
    payload = {
        "name": "New Book",
        "author": "New Author",
        "price": 150,
        "stock": 5
    }
    response = api_client.post(url, payload)

    assert response.status_code == 403
    assert response.data['error'] == "You do not have permission to perform this action."

@pytest.mark.django_db
def test_update_book_as_superuser(api_client, superuser, book):
    """Test updating a book as a superuser."""
    token = RefreshToken.for_user(superuser).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    url = reverse('books-detail', args=[book.id])
    payload = {
        "name": "Updated Book",
        "author": "Updated Author",
        "price": 200,
        "stock": 20
    }
    response = api_client.put(url, payload)

    assert response.status_code == 200
    assert response.data['message'] == "Book updated successfully"
    assert response.data['data']['name'] == "Updated Book"

@pytest.mark.django_db
def test_delete_book_as_superuser(api_client, superuser, book):
    """Test deleting a book as a superuser."""
    token = RefreshToken.for_user(superuser).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    url = reverse('books-detail', args=[book.id])
    response = api_client.delete(url)

    assert response.status_code == 204


@pytest.mark.django_db
def test_delete_book_as_regular_user(api_client, regular_user, book):
    """Test deleting a book as a regular user."""
    token = RefreshToken.for_user(regular_user).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    url = reverse('books-detail', args=[book.id])
    response = api_client.delete(url)

    assert response.status_code == 403
    assert response.data['error'] == "You do not have permission to perform this action."