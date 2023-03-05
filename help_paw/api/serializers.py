import re

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from info.models import FAQ, HelpArticle, News, Vacancy
from shelters.models import AnimalType, Pet, Shelter

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password')


class CustomUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'subscription_pet',
            'subscription_shelter', 'status'
        )
        read_only_fields = ('status',)


class NewsShortSerializer(serializers.ModelSerializer):
    shelter = serializers.CharField(source='shelter.name', default=None)

    class Meta:
        fields = ('id', 'header', 'pub_date', 'profile_image', 'shelter')
        model = News


class NewsSerializer(serializers.ModelSerializer):
    profile_image = Base64ImageField()
    image_1 = Base64ImageField(required=False, allow_null=True)
    image_2 = Base64ImageField(required=False, allow_null=True)
    image_3 = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = '__all__'
        model = News


class FAQSerializer(serializers.ModelSerializer):
    """Ответы на часто задаваемые вопросы"""
    class Meta:
        fields = ('id', 'question', 'answer')
        model = FAQ


class HelpArticleSerializer(serializers.ModelSerializer):
    profile_image = Base64ImageField(required=True)
    header = serializers.CharField(max_length=50)

    class Meta:
        fields = (
            'id', 'header', 'text', 'pub_date', 'profile_image', 'source'
        )
        model = HelpArticle

    def validate_header(self, value):
        if value.isdigit():
            raise ValidationError('Название не может содержать только цифры')
        return value


class HelpArticleShortSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'header', 'profile_image')
        model = HelpArticle


class ShelterShortSerializer(serializers.ModelSerializer):
    working_from_hour = serializers.TimeField(format='%H:%M')
    working_to_hour = serializers.TimeField(format='%H:%M')

    class Meta:
        fields = (
            'id', 'name', 'address', 'working_from_hour', 'working_to_hour',
            'logo', 'profile_image', 'long', 'lat'
        )
        model = Shelter


class ShelterSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    logo = Base64ImageField(required=False, allow_null=True)
    profile_image = Base64ImageField(required=False, allow_null=True)
    animal_types = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=AnimalType.objects.all()
    )
    money_collected = serializers.SerializerMethodField(read_only=True)
    animals_adopted = serializers.SerializerMethodField(read_only=True)
    working_from_hour = serializers.TimeField(format='%H:%M')
    working_to_hour = serializers.TimeField(format='%H:%M')
    vk_page = serializers.URLField(required=False)
    ok_page = serializers.URLField(required=False)
    telegram = serializers.URLField(required=False)

    class Meta:
        exclude = ('is_approved', )
        model = Shelter

    def get_money_collected(self, obj):
        return 0

    def get_animals_adopted(self, obj):
        return obj.pets.filter(is_adopted=True).count()

    def validate_vk_page(self, value):
        if not re.match('https://vk.com/', value):
            raise ValidationError('Адрес должен начинаться с https://vk.com/')
        return value

    def validate_ok_page(self, value):
        if not re.match('https://ok.ru/', value):
            raise ValidationError('Адрес должен начинаться с https://ok.ru/')
        return value

    def validate_telegram(self, value):
        if not re.match('https://t.me/', value):
            raise ValidationError('Адрес должен начинаться с https://t.me/')
        return value

    def validate(self, attrs):
        if Shelter.objects.filter(owner=self.context.get('user')).exists():
            raise serializers.ValidationError(
                'Пользователь может зарегистрировать только один приют')
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


class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'shelter', 'salary', 'schedule', 'position', 'description',
        )
        model = Vacancy


class AnimalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug',)
        model = AnimalType
