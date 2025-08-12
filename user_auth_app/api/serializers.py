from django.contrib.auth.models import User
from rest_framework import serializers

class UserAccountSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return f"{obj.username}".strip()
    

class RegistrationSerializer(serializers.ModelSerializer):
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
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value


    def create(self, validated_data):
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
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
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