from rest_framework import generics
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer # ,RegistrationSerializer

class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer