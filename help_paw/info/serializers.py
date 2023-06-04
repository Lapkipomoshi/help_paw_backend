from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.serializers import ShelterTestSerializer
from info.models import News, Vacancy


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


class NewsShortSerializer(serializers.ModelSerializer):
    shelter = ShelterTestSerializer(read_only=True, default=None)
    pub_date = serializers.DateTimeField(read_only=True, format='%Y-%m-%d')

    class Meta:
        fields = (
            'id', 'header', 'pub_date', 'profile_image', 'shelter',
        )
        model = News


class VacancySerializer(serializers.ModelSerializer):
    is_closed = serializers.BooleanField(read_only=True)

    class Meta:
        fields = (
            'id', 'salary', 'is_ndfl', 'education', 'schedule', 'position',
            'description', 'pub_date', 'is_closed',
        )
        model = Vacancy
