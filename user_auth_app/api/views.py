from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def post(self, request):
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