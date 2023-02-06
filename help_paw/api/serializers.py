from drf_base64.fields import Base64ImageField
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
    profile_image = Base64ImageField(required=True)

    class Meta:
        fields = (
            'id', 'header', 'text', 'pub_date', 'profile_image', 'source'
        )
        model = HelpArticle


class HelpArticleShortSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'header', 'profile_image')
        model = HelpArticle


class ShelterShortSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'name', 'address', 'working_hours', 'logo', 'profile_image',
            'long', 'lat'
        )
        model = Shelter


class ShelterSerializer(serializers.ModelSerializer):
    owner = serializers.IntegerField(source='owner.id', read_only=True)
    logo = Base64ImageField(required=False)
    profile_image = Base64ImageField(required=False)

    class Meta:
        exclude = ('is_approved', 'long', 'lat')
        model = Shelter

    def validate(self, attrs):
        if Shelter.objects.filter(owner=self.context.get('user')).exists():
            raise serializers.ValidationError(
                'Пользователь может зарегистрировать только один приют'
            )
        return attrs
