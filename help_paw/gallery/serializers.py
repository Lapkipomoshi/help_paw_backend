from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from gallery.models import MAX_IMAGE_SIZE, Image


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
