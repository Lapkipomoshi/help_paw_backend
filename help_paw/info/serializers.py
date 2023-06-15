from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from info.models import (FAQ, MAX_IMAGE_CNT, MAX_IMAGE_SIZE, HelpArticle,
                         Image, News, Vacancy)
from shelters.serializers import ShelterTestSerializer


class VacancySerializer(serializers.ModelSerializer):
    is_closed = serializers.BooleanField(read_only=True)

    class Meta:
        fields = (
            'id', 'salary', 'is_ndfl', 'education', 'schedule', 'position',
            'description', 'pub_date', 'is_closed',
        )
        model = Vacancy


class ImageSerializer(serializers.Serializer):
    image = Base64ImageField()

    class Meta:
        fields = ('image',)
        model = Image


class ImageValidator:

    def __call__(self, value):
        if not self.is_valid(value):
            raise serializers.ValidationError(
                f'Размер изображения не должен превышать {MAX_IMAGE_SIZE} МБ')

    def is_valid(self, value):
        image = value.get('image')
        if image and image.size > MAX_IMAGE_SIZE:
            return False
        return True


class ArticleSerializer(serializers.ModelSerializer):
    profile_image = Base64ImageField()
    pub_date = serializers.DateTimeField(read_only=True, format='%Y-%m-%d')
    gallery = ImageSerializer(many=True, required=False,
                              validators=[ImageValidator()])

    def validate(self, attrs):
        gallery = attrs.get('gallery')
        if gallery and len(gallery) > MAX_IMAGE_CNT:
            raise serializers.ValidationError(
                f'Максимальное количество изображений '
                f'в галерее - {MAX_IMAGE_CNT}')
        return attrs

    def validate_header(self, value):
        if value.isdigit():
            raise serializers.ValidationError(
                'Название не может содержать только цифры'
            )
        return value

    def create(self, validated_data):
        gallery = validated_data.pop('gallery', [])

        if isinstance(self, NewsSerializer):
            instance = News.objects.create(**validated_data)
        elif isinstance(self, HelpArticleSerializer):
            instance = HelpArticle.objects.create(**validated_data)
        else:
            raise NotImplementedError('Неподдерживаемый сериализатор')

        objects = [Image(**image) for image in gallery]
        images = Image.objects.bulk_create(objects)
        instance.gallery.add(*images)

        return instance

    def clear_gallery(self, instance):
        for image in instance.gallery.all():

            if isinstance(self, NewsSerializer):
                objects = image.news_related.all()
            elif isinstance(self, HelpArticleSerializer):
                objects = image.helparticle_related.all()
            else:
                raise NotImplementedError('Неподдерживаемый сериализатор')

            if len(objects) == 1 and objects[0] == instance:
                image.delete()

    def update(self, instance, validated_data):
        gallery = validated_data.pop('gallery', None)

        if gallery is not None:
            self.clear_gallery(instance)
            objects = [Image(**image) for image in gallery]
            images = Image.objects.bulk_create(objects)
            instance.gallery.add(*images)

        return super().update(instance, validated_data)


class NewsSerializer(ArticleSerializer):
    shelter = ShelterTestSerializer(read_only=True, default=None)

    class Meta:
        fields = (
            'id', 'profile_image', 'gallery', 'header', 'text', 'pub_date',
            'shelter',
        )
        model = News


class NewsShortSerializer(ArticleSerializer):
    shelter = ShelterTestSerializer(read_only=True, default=None)

    class Meta:
        fields = (
            'id', 'header', 'pub_date', 'profile_image', 'shelter',
        )
        model = News


class HelpArticleSerializer(ArticleSerializer):
    class Meta:
        fields = (
            'id', 'header', 'text', 'pub_date', 'gallery', 'profile_image',
            'source',
        )
        model = HelpArticle


class HelpArticleShortSerializer(ArticleSerializer):
    class Meta:
        fields = ('id', 'header', 'profile_image',)
        model = HelpArticle


class FAQSerializer(serializers.ModelSerializer):
    """Ответы на часто задаваемые вопросы"""

    class Meta:
        fields = ('id', 'question', 'answer',)
        model = FAQ
