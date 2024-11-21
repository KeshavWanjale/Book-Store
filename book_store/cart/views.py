from .models import CartItems,CartModel
from .serializers import CartSerializer
from rest_framework  import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from book.models import Book
from django.db import models
from loguru import logger

class CartsViews(APIView):
    """
    Handles operations related to the user's shopping cart.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Retrieve the active cart for the authenticated user")
    def get(self,request):
        """
        Description:
            Retrieves the active cart for the authenticated user.
        Parameters:
            request (Request): The request object from the authenticated user.
        Returns:
            Response: A response containing the active cart or an error message.
        """
        try:
            active_cart = CartModel.objects.get(user=request.user,is_ordered=False)
            if  active_cart :
                cart_serializer = CartSerializer(active_cart)
                logger.info("The active cart of the user is Fetched")
                return Response({"message":"The active cart of the user is Fetched","status":"success","cart":cart_serializer.data},status=status.HTTP_200_OK)
        except CartModel.DoesNotExist:
            logger.error("No active cart found for the user")
            return Response({
                    "message": "No active cart found for the user",
                    "status": "error"
                },status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                logger.error(f"An unexpected error occurred: {str(e)}")
                return Response({
                    "message": "An unexpected error occurred",
                    "status": "error",
                    "error": str(e)
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_summary="Add or update items in the cart",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'book_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the book to add'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity of the book to add')
            },required=['book_id', 'quantity'])
    )
    def post(self,request):
        """
        Description:
            Adds or updates items in the authenticated user's active cart.
        Parameters:
            request (Request): The request object containing book ID and quantity.
        Returns:
            Response: A response with the updated cart details or an error message.
        """
        try:
            book_id = request.data.get('book_id')
            quantity = request.data.get('quantity')
            if not book_id or not quantity:
                logger.error("book_id and quantity are required.")
                return Response({"message": "book_id and quantity are required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                book = Book.objects.get(id=book_id)
            except Book.DoesNotExist:
                logger.error("Book does not exist in the database.")
                return Response({"message": "Book does not exist in the database."}, status=status.HTTP_404_NOT_FOUND)

            if book.stock < quantity:
                logger.error("Insufficient stock.")
                return Response({"message": f"Insufficient stock. Only {book.stock} available."}, status=status.HTTP_400_BAD_REQUEST)

            active_cart, _ = CartModel.objects.get_or_create(user=request.user, is_ordered=False)

            cart_item, created = CartItems.objects.get_or_create(cart=active_cart, book=book)
            if created:
                cart_item.quantity = quantity
            else:
                new_quantity = cart_item.quantity + quantity
                if book.stock < new_quantity:
                    logger.error("Insufficient stock.")
                    return Response({"message": f"Insufficient stock. Only {book.stock} available."}, status=status.HTTP_400_BAD_REQUEST)
                cart_item.quantity = new_quantity

            cart_item.price = book.price * cart_item.quantity
            cart_item.save()

            totals = CartItems.objects.filter(cart=active_cart).aggregate(
                total_quantity=models.Sum('quantity'),
                total_price=models.Sum('price')
            )
            active_cart.total_quantity = totals['total_quantity'] or 0
            active_cart.total_price = totals['total_price'] or 0
            active_cart.save()

            cart_serializer = CartSerializer(active_cart)
            
            logger.info("Cart updated successfully" if not created else "New cart created successfully")
            return Response({
                    "message": "Cart updated successfully" if not created else "New cart created successfully",
                    "status": "success",
                    "cart": cart_serializer.data,
                },status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return Response(
                {
                    "message": "An error occurred while processing the request.",
                    "status": "error",
                    "error": str(e),
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CartsViewsByID(APIView):
    """
    Handles operations on specific items within the user's shopping cart.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Delete the active cart")
    def delete(self, request, pk=None, *args, **kwargs):
        """
        Description:
            Deletes a specific item from the user's active cart.
        Parameters:
            request (Request): The request object from the authenticated user.
            pk (int): The primary key of the item to be removed.
        Returns:
            Response: A response indicating success or failure of the operation.
        """
        try:
            if pk:
                active_cart = CartModel.objects.filter(user=request.user, is_ordered=False).first()
                if not active_cart:
                    logger.error("No active cart found.")
                    return Response({"message": "No active cart found."}, status=status.HTTP_404_NOT_FOUND)

                cart_item = CartItems.objects.filter(book_id=pk, cart=active_cart).first()
                if not cart_item:
                    logger.error("No such item found in the active cart.")
                    return Response({"message": "No such item found in the active cart."}, status=status.HTTP_404_NOT_FOUND)

                cart_item.delete()

                totals = CartItems.objects.filter(cart=active_cart).aggregate(
                    total_quantity=models.Sum('quantity'),
                    total_price=models.Sum('price')
                )
                active_cart.total_quantity = totals['total_quantity'] or 0
                active_cart.total_price = totals['total_price'] or 0
                active_cart.save()
                logger.info("Item deleted successfully")
                return Response({"message": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                logger.error("Order ID is required.")
                return Response({"message": "Item ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return Response({"message": "An unexpected error occurred.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class OrderViews(APIView):
    """
    Handles operations related to user orders.
    """

    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(operation_summary="Retrieve order details")
    def get(self,request):
        """
        Description:
            Retrieves a list of all orders placed by the authenticated user.
        Parameters:
            request (Request): The request object from the authenticated user.
        Returns:
            Response: A response containing the order details or an error message.
        """
        try:
            ordered_cart=CartModel.objects.filter(user=request.user, is_ordered=True)

            if not ordered_cart.exists():
                logger.error("No order Found")
                return Response({"message": "No order Found","status":"Error"},status=status.HTTP_404_NOT_FOUND)
            
            serializer=CartSerializer(ordered_cart,many=True)
            logger.info("Order details fetched successfully.")
            return Response({"message": "Order details fetched successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return Response({"message": "An error occurred while retrieving the orders.", "error": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_summary="Place an order")
    def post(self,request,*args,**kwargs):
        """
        Description:
            Places an order for the items in the authenticated user's active cart.
        Parameters:
            request (Request): The request object from the authenticated user.
        Returns:
            Response: A response indicating success or failure of the order placement.
        """
        try:
            active_cart=CartModel.objects.filter(user=request.user,is_ordered=False).first()

            if active_cart:
                cart_items=CartItems.objects.filter(cart=active_cart)
                if not cart_items.exists():
                    logger.error("The cart is empty.")
                    return Response({"message": "The cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

                for item in cart_items:
                    if item.quantity>item.book.stock:
                        logger.error("Insufficient stock for the book ")
                        return Response({"message": f"Insufficient stock for the book {item.book.name}."},status=status.HTTP_400_BAD_REQUEST)
                    book = item.book
                    book.stock -= item.quantity
                    book.save()
                    
                active_cart.is_ordered = True
                active_cart.save()

                logger.info("The order placed")
                return Response({"message":"The order placed","status":"Success"},status=status.HTTP_200_OK)
            
            return Response({"message": "No active cart to order."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return Response(
                {"message": "An error occurred during the ordering process.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class OrderViewsByID(APIView):
    """
    Handles operations on specific orders.
    """

    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    
    @swagger_auto_schema(operation_summary="Cancel an order")
    def delete(self,request,pk):
        
        try:
            ordered_cart = CartModel.objects.filter(user=request.user, is_ordered=True, id=pk)
            if not ordered_cart:
                logger.error("No order found to cancel.")
                return Response({"message": "No order found to cancel."}, status=status.HTTP_404_NOT_FOUND)

            cart_items = CartItems.objects.filter(cart=ordered_cart)
            
            for item in cart_items:
                book=item.book
                book.stock+=item.quantity
                book.save()
            ordered_cart.delete()
            logger.info("Order cancelled successfully.")
            return Response({"message": "Order cancelled successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return Response({"message": "An error occurred while cancelling the order.", "error": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
