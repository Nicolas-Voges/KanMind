"""
API views for user registration and authentication.

This module provides:
- RegistrationView: Allows new users to register and receive an auth token.
- CustomLoginView: Authenticates existing users and returns an auth token.
"""


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .serializers import RegistrationSerializer, LoginSerializer


class RegistrationView(APIView):
    """
    API view for registering a new user.

    Accepts user details, creates the account, and returns an authentication token.
    """


    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST request to register a new user.

        Returns:
            - Auth token
            - Full name
            - Email
            - User ID
        If validation fails, returns the serializer errors.
        """
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            save_account = serializer.save()
            token, created = Token.objects.get_or_create(user=save_account)
            data = {
                'token': token.key,
                'fullname': save_account.username,
                'email': save_account.email,
                'user_id': save_account.id
            }
        else:
            data = serializer.errors

        return Response(data)
    

class CustomLoginView(APIView):
    """
    API view for authenticating a user and returning an auth token.
    """


    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        """
        Handle POST request to log in a user.

        Returns:
            - Auth token
            - Full name
            - Email
            - User ID
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'fullname': user.username,
            'email': user.email,
            'user_id': user.id
        })