import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from djoser.serializers import (UidAndTokenSerializer, UserCreateSerializer,
                                UserSerializer)
from rest_framework import serializers

from shelters.serializers import ShelterShortSerializer

User = get_user_model()


class EmailResetConfirmSerializer(UidAndTokenSerializer):
    new_email = serializers.SerializerMethodField()

    def get_new_email(self, obj):
        try:
            decode = jwt.decode(
                self.initial_data['new_email'],
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            raise serializers.ValidationError(
                'Токен не валиден или время действия истекло')
        return decode.get('email')


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password',)


class CustomUserSerializer(UserSerializer):
    email = serializers.EmailField(read_only=True)
    own_shelter = ShelterShortSerializer(read_only=True, source='shelter')

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'status', 'donations_sum', 'own_shelter',
        )
        read_only_fields = ('status', 'donations_sum',)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует')
        return value
