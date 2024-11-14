from rest_framework import serializers
from .models import CustomUser
from .utils import validate_email,validate_password,validate_username


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Description:
        Serializer for user registration. Validates email, username, and password formats.
    Fields:
        id (int): The unique identifier for the user.
        email (str): The email address of the user.
        username (str): The username of the user.
        password (str): The password for the user account (write-only).
    Methods:
        validate (dict): Validates email, username, and password formats.
        create (CustomUser): Creates and returns a new user instance.
    """
    class Meta:
        model = CustomUser
        fields = ["id","email", "username", "password"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        """
        Description:
            Validate email, username, and password formats using custom validation utilities.
        Parameter:
            data (dict): Dictionary containing email, username, and password to validate.
        Returns:
            dict: The validated data if successful.
        Raises:
            serializers.ValidationError: If any field fails validation checks.
        """
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")

        if not validate_email(email):
            raise serializers.ValidationError("Invalid Email format")
        if not validate_username(username):
            raise serializers.ValidationError("Invalid Username format")
        if not validate_password(password):
            raise serializers.ValidationError("Invalid Password format")

        return data
    
    def create(self, validated_data):
        """
        Description:
            Create a new user instance with validated data.
        Parameter:
            validated_data (dict): Dictionary containing validated data for user creation.
        Returns:
            CustomUser: The newly created user instance.
        """
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    
class UserLoginSerializer(serializers.Serializer):
    """
    Description:
        Serializer for user login. Validates the presence of email and password.
    Fields:
        email (str): The email address of the user attempting to log in.
        password (str): The password for the user account (write-only).
    Methods:
        validate (dict): Ensures email and password fields are provided.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Description:
            Validate the presence of email and password in login data.
        Parameter:
            data (dict): Dictionary containing email and password.
        Returns:
            dict: The validated data if both fields are present.
        Raises:
            serializers.ValidationError: If email or password is missing.
        """
        email = data.get("email")
        password = data.get("password")

        if not email:
            raise serializers.ValidationError("Email is required")
        if not password:
            raise serializers.ValidationError("Password is required")

        return data