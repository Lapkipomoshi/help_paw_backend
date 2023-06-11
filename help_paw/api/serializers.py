import random

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from djoser.serializers import (UidAndTokenSerializer, UserCreateSerializer,
                                UserSerializer)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from info.models import FAQ, HelpArticle, News
from shelters.models import AnimalType, Pet, Shelter

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

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'subscription_pet',
            'subscription_shelter', 'status',
        )
        read_only_fields = ('status',)


class ShelterTestSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name',)
        model = Shelter


class NewsShortSerializer(serializers.ModelSerializer):
    shelter = ShelterTestSerializer(read_only=True, default=None)
    pub_date = serializers.DateTimeField(read_only=True, format='%Y-%m-%d')

    class Meta:
        fields = (
            'id', 'header', 'pub_date', 'profile_image', 'shelter',
        )
        model = News


class NewsSerializer(serializers.ModelSerializer):
    profile_image = Base64ImageField()
    image_1 = Base64ImageField(required=False, allow_null=True)
    image_2 = Base64ImageField(required=False, allow_null=True)
    image_3 = Base64ImageField(required=False, allow_null=True)
    pub_date = serializers.DateTimeField(read_only=True, format='%Y-%m-%d')
    shelter = ShelterTestSerializer(read_only=True, default=None)

    class Meta:
        fields = (
            'id', 'profile_image', 'image_1', 'image_2', 'image_3', 'header',
            'text', 'pub_date', 'shelter',
        )
        model = News


class FAQSerializer(serializers.ModelSerializer):
    """Ответы на часто задаваемые вопросы"""
    class Meta:
        fields = ('id', 'question', 'answer',)
        model = FAQ


class HelpArticleSerializer(serializers.ModelSerializer):
    profile_image = Base64ImageField(required=True)
    header = serializers.CharField(max_length=50)

    class Meta:
        fields = (
            'id', 'header', 'text', 'pub_date', 'profile_image', 'source',
        )
        model = HelpArticle

    def validate_header(self, value):
        if value.isdigit():
            raise serializers.ValidationError('Название не может содержать только цифры')
        return value


class HelpArticleShortSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'header', 'profile_image',)
        model = HelpArticle


class ShelterShortSerializer(serializers.ModelSerializer):
    working_from_hour = serializers.TimeField(format='%H:%M')
    working_to_hour = serializers.TimeField(format='%H:%M')
    warning = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'address', 'working_from_hour', 'working_to_hour',
            'logo', 'profile_image', 'long', 'lat', 'warning',
        )
        model = Shelter

    def get_warning(self, obj):
        return random.choice(['red', 'yellow', 'green'])


class ShelterSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    logo = Base64ImageField(required=False, allow_null=True)
    profile_image = Base64ImageField(required=False, allow_null=True)
    animal_types = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=AnimalType.objects.all(),
        allow_empty=False
    )
    money_collected = serializers.SerializerMethodField(read_only=True)
    animals_adopted = serializers.SerializerMethodField(read_only=True)
    working_from_hour = serializers.TimeField(format='%H:%M')
    working_to_hour = serializers.TimeField(format='%H:%M')

    class Meta:
        exclude = ('is_approved', )
        model = Shelter

    def get_money_collected(self, obj):
        return 0

    def get_animals_adopted(self, obj):
        return obj.pets.filter(is_adopted=True).count()

    def validate(self, attrs):
        user = self.context['request'].user
        if Shelter.objects.filter(owner=user).exists():
            raise serializers.ValidationError(
                'Пользователь может зарегистрировать только один приют')
        if not user.is_user:
            raise serializers.ValidationError(
                'Администраторам и модераторам нельзя регистрировать приюты')
        return attrs


class PetSerializer(serializers.ModelSerializer):
    animal_type = serializers.SlugRelatedField(
        slug_field='slug', queryset=AnimalType.objects.all()
    )
    age = serializers.IntegerField(default=0)
    photo = Base64ImageField()
    is_adopted = serializers.BooleanField(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'animal_type', 'sex', 'age', 'about', 'shelter',
            'photo', 'is_adopted',
        )
        model = Pet


class AnimalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug',)
        model = AnimalType


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
