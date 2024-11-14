from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.decorators import api_view
from .models import CustomUser
from rest_framework.reverse import reverse
from .tasks import send_verification_mail
from loguru import logger


class RegisterUser(APIView):

    @swagger_auto_schema(operation_description="register user", request_body=UserRegistrationSerializer)
    def post(self, request):
        """
        Description:
            Register a new user with provided data, send verification email with URL.
        Parameter:
            request (Request): The request object containing user registration data.
        Returns:
            Response: A response indicating success or failure of the registration.
        """
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)

                token = str(refresh.access_token)
                verification_url = request.build_absolute_uri(
                    reverse('verify', kwargs={'token': token})
                )
                subject = 'Verify your account'
                message = f'Hi {user.username},\n\nPlease verify your account using the link below:\n{verification_url}'
                recipient_list = [user.email]
                
                send_verification_mail.delay(subject, message, recipient_list)
                logger.info("User registered successfully")
                return Response({
                    "message": "User registered successfully, Please Verify Email!!!",
                    "status": "success",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            
            logger.error(f"Unexpected error occurred: {serializer.errors}")
            return Response({"message": "Unexpected error occurred", "status": "error", "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Unexpected error occurred: {str(e)}")
            return Response({"message": "An internal error occurred", "status": "error", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginUser(APIView):

    @swagger_auto_schema(operation_description="user login", request_body=UserLoginSerializer)
    def post(self, request):
        """
        Description:
        Authenticate user credentials and return JWT tokens for valid login.
        Parameter:
            request (Request): The request object containing user login data.
        Returns:
            Response: A response with JWT access and refresh tokens if login is successful.
        """
        try:
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']
                user = authenticate(email=email, password=password)

                if user is not None:
                    refresh = RefreshToken.for_user(user)
                    logger.info("Login successful!")
                    return Response({
                        "message": "Login successful!", 
                        "status": "success", 
                        "data": serializer.data,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    })
                
                logger.error("Invalid email or password")
                return Response({"message": "Login failed", "error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)
            logger.error(f"Unexpected error occurred {serializer.errors}")
            return Response({"message": "Unexpected error occurred", "status": "error", "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error occurred: {str(e)}")
            return Response({"message": "An internal error occurred", "status": "error", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def verify_registered_user(request, token):
    """
    Description:
        Verify a user's account by decoding the token and updating the verification status.
    Parameter:
        request (Request): The request object from the verification link.
        token (str): The token included in the verification URL.
    Returns:
        Response: A response indicating whether the user verification was successful.
    """
    try:
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        user = CustomUser.objects.get(id=user_id)

        if not user.is_verified:
            user.is_verified = True
            user.save()
        logger.info("User verification successful")
        return Response({"message": "User verification successful", "status": "success"}, status=status.HTTP_200_OK)

    except CustomUser.DoesNotExist:
        logger.error(f"User not found")
        return Response({"message": "User not found", "status": "error"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        return Response({"message": "Invalid or expired token", "status": "error", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
