"""
Serializers for user authentication and account management.

This module provides serializers for:
- Viewing basic user account data.
- Registering new users with password confirmation.
- Authenticating users via email and password.
"""


from django.contrib.auth.models import User
from rest_framework import serializers

class UserAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving basic user account details.
    """
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        """
        Return the full name for the user.

        Currently uses the username field as the full name.
        """
        return f"{obj.username}".strip()
    

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user account.

    Includes fields for full name, email, password, and password confirmation.
    """


    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'fullname',
            'email',
            'password',
            'repeated_password'
        ]
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }
        

    def validate_email(self, value):
        """
        Ensure the email address is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value


    def create(self, validated_data):
        """
        Create a new user instance after validating matching passwords.
        """
        fullname = validated_data.pop('fullname')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        repeated_password = validated_data.pop('repeated_password')

        if password != repeated_password:
            raise serializers.ValidationError("Passwords do not match")
        
        user = User.objects.create_user(
            username=fullname,
            email=email,
            password=password
        )
        return user
    

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login using email and password.
    """


    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Validate email and password combination.

        Raises a validation error if:
        - Email or password is missing.
        - User does not exist.
        - Password does not match.
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError('Both email and password are required')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email or password')

        if not user.check_password(password):
            raise serializers.ValidationError('Invalid email or password')

        attrs['user'] = user
        return attrs