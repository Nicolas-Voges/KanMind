from django.contrib.auth.models import User
from rest_framework import serializers
from user_auth_app.models import UserAccount

class UserAccountSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(source='user.email')
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        # return f"{obj.first_name} {obj.last_name}".strip()
        return f"{obj.username}".strip()