from django.contrib.auth.models import User
from rest_framework import serializers

class UserAccountSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(source='user.email')
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        # return f"{obj.first_name} {obj.last_name}".strip()
        return f"{obj.username}".strip()
    

class RegistrationSerializer(serializers.ModelSerializer):
    
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

    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        
        if pw != repeated_pw:
            raise serializers.ValidationError('Password dont match')
        
        account = User(email=self.validated_data['email'], username=self.validated_data['username'])
        account.set_password(pw)
        account.save()
        return account