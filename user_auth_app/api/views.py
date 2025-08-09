from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from user_auth_app.models import UserAccount
from .serializers import UserAccountSerializer, RegistrationSerializer

class UserProfileList(generics.ListCreateAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer


class RegistrationView(APIView):
    queryset = UserAccount.objects.all()
    # serializer_class = UserAccountSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            save_account = serializer.save()
            token, createdt = Token.objects.get_or_create(user=save_account)
            data = {
                'token': token.key,
                'username': save_account.username,
                'email': save_account.email
            }
        else:
            data = serializer.errors

        return Response(data)