from rest_framework import serializers

from info.models import FAQ, HelpArticle, News
from shelters.models import Shelter


class NewsSerializer(serializers.ModelSerializer):
    """Новости приютов"""
    class Meta:
        fields = (
            'header', 'text', 'pub_date', 'profile_image', 'image_1',
            'image_2', 'image_3', 'shelter'
        )
        model = News


class FAQSerializer(serializers.ModelSerializer):
    """Ответы на часто задаваемые вопросы"""
    class Meta:
        fields = ('question', 'answer')
        model = FAQ


class HelpArticleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('header', 'text', 'pub_date', 'profile_image', 'source')
        model = HelpArticle


class HelpArticleShortSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('header', 'profile_image')
        model = HelpArticle


class ShelterShortSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name', 'address', 'working_hours', 'logo', 'profile_image',
            'long', 'lat'
        )
        model = Shelter


class ShelterSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('is_approved', 'long', 'lat')
        model = Shelter


class ShelterWriteSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('is_approved', 'long', 'lat')
        model = Shelter
