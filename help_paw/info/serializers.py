from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from gallery.models import MAX_IMAGE_CNT, Image
from gallery.serializers import ImageSerializer, ImageValidator
from info.models import FAQ, Education, HelpArticle, News, Schedule, Vacancy
from shelters.serializers import ShelterNameSerializer


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('slug', 'name')
        model = Schedule


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('slug', 'name')
        model = Education


class VacancyReadSerializer(serializers.ModelSerializer):
    is_closed = serializers.BooleanField(read_only=True)
    education = EducationSerializer()
    schedule = ScheduleSerializer(many=True)

    class Meta:
        fields = (
            'id', 'salary', 'is_ndfl', 'education', 'schedule', 'position',
            'description', 'pub_date', 'is_closed',
        )
        model = Vacancy


class VacancyWriteSerializer(VacancyReadSerializer):
    education = serializers.SlugRelatedField(
        slug_field='slug', queryset=Education.objects.all()
    )
    schedule = serializers.SlugRelatedField(
        slug_field='slug', queryset=Schedule.objects.all(), many=True
    )


class ArticleSerializer(serializers.ModelSerializer):
    profile_image = Base64ImageField()
    pub_date = serializers.DateTimeField(read_only=True, format='%d.%m.%Y')
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
        else:
            instance = HelpArticle.objects.create(**validated_data)

        objects = [Image(**image) for image in gallery]
        images = Image.objects.bulk_create(objects)
        instance.gallery.add(*images)

        return instance

    def clear_gallery(self, instance):
        for image in instance.gallery.all():

            if isinstance(self, NewsSerializer):
                objects = image.news_related.all()
            else:
                objects = image.helparticle_related.all()

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
    shelter = ShelterNameSerializer(read_only=True, default=None)

    class Meta:
        fields = (
            'id', 'profile_image', 'gallery', 'header', 'text', 'pub_date',
            'shelter',
        )
        model = News


class NewsShortSerializer(ArticleSerializer):
    shelter = ShelterNameSerializer(read_only=True, default=None)

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
