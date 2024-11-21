from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from loguru import logger
from drf_yasg.utils import swagger_auto_schema


class BookViewset(viewsets.ModelViewSet):
    """
    Description:
        ViewSet for managing Book objects. Provides CRUD operations with authentication and permissions.
        Only superusers can perform create, update, and delete operations. All authenticated users can list books.
    Attributes:
        queryset (QuerySet): QuerySet for retrieving all Book objects.
        serializer_class (Serializer): The serializer class for the Book model.
        permission_classes (list): Permissions required for accessing this ViewSet.
        authentication_classes (list): Authentication classes for this ViewSet.
    Methods:
        list (Response): Retrieves a list of all books.
        create (Response): Creates a new book.
        update (Response): Updates an existing book.
        destroy (Response): Deletes an existing book.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(operation_description="List Books")   
    def list(self, request, *args, **kwargs):
        """
        Description:
            Retrieves a list of all books.
        Parameters:
            request (Request): The request object from the authenticated user.
        Returns:
            Response: A response containing a list of books or an error message.
        """
        try:
            response = super().list(request, *args, **kwargs)
            logger.info("Books retrieved successfully")
            return response
        except Exception as e:
            logger.error(f"Error retrieving books: {str(e)}")
            return Response({'error': f"Error retrieving books: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(operation_description="Create Book",request_body=BookSerializer)
    def create(self, request, *args, **kwargs):
        """
        Description:
            Creates a new book. Only superusers are allowed to perform this action.
        Parameters:
            request (Request): The request object containing book details.
        Returns:
            Response: A response with success or error message and the created book data.
        Raises:
            ValidationError: If the input data is invalid.
            PermissionDenied: If the user is not a superuser.
        """
        if not request.user.is_superuser:
            logger.error("You do not have permission to perform this action")
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        try:
            serializer=self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            logger.info("Book created successfully")
            return Response({"message": "Book created successfully", "status": "Success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        
        except ValidationError as ve:
            logger.error("Invalid data")
            return Response({'error': f'Invalid data: {ve.detail}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating book {str(e)}")
            return Response({'error': f'Error creating book: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(operation_description="Update Book", request_body=BookSerializer)
    def update(self, request, *args, **kwargs):
        """
        Description:
            Updates an existing book. Only superusers are allowed to perform this action.
        Parameters:
            request (Request): The request object containing updated book details.
        Returns:
            Response: A response with success or error message and the updated book data.
        Raises:
            NotFound: If the book does not exist.
            ValidationError: If the input data is invalid.
            PermissionDenied: If the user is not a superuser.
        """
        if not request.user.is_superuser :
            logger.error("You do not have permission to perform this action.")
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        try:
            book = self.get_object()
            serializer = self.get_serializer(book, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Book updated successfully", "status": "Success", "data": serializer.data}, status=status.HTTP_200_OK)
        except NotFound:
            return Response({'error': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ve:
            return Response({'error': f'Invalid data: {ve.detail}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error updating book: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(operation_description="Delete Book")
    def destroy(self, request, *args, **kwargs):
        """
        Description:
            Deletes an existing book. Only superusers are allowed to perform this action.
        Parameters:
            request (Request): The request object specifying the book to delete.
        Returns:
            Response: A response with a success or error message.
        Raises:
            NotFound: If the book does not exist.
            PermissionDenied: If the user is not a superuser.
        """
        if not request.user.is_superuser:
            logger.error("Permission denied for deleting a book")
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        try:
            response = super().destroy(request, *args, **kwargs)
            logger.info(f"Book deleted successfully")
            return response
        except NotFound:
            logger.error("Book not found for deletion")
            return Response({'error': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting book: {str(e)}")
            return Response({'error': f"Error deleting book: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
