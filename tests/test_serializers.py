import base64
import json

import factory
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from gallery.models import MAX_IMAGE_CNT, MAX_IMAGE_SIZE
from gallery.serializers import ImageValidator
from info.serializers import HelpArticleSerializer, NewsSerializer
from rest_framework.exceptions import ValidationError
from shelters.serializers import ShelterSerializer
from users.serializers import EmailSerializer

from tests.plugins.methods import get_image_data

fake = Faker()
pytestmark = pytest.mark.django_db(transaction=True)


class TestSerializers:

    def test_help_article_serializer(self, help_article_factory):
        must_fail_header = '666'
        valid_header = 'ABC'

        payload = factory.build(
            dict,
            FACTORY_CLASS=help_article_factory,
            header=must_fail_header,
        )

        serializer = HelpArticleSerializer(data=payload)

        assert not serializer.is_valid()
        assert 'header' in serializer.errors.keys()

        payload = factory.build(
            dict,
            FACTORY_CLASS=help_article_factory,
            header=valid_header,
        )

        serializer = HelpArticleSerializer(data=payload)

        assert serializer.is_valid()

        my_help = serializer.save()
        assert my_help.header == valid_header

    def test_shelter_serializer(self, user, rf, user_factory, shelter_factory,
                                animal_type_factory):
        endpoint = '/api/v1/shelters/'
        my_shelter = shelter_factory.create()
        my_types = animal_type_factory.create_batch(3)

        payload = factory.build(
            dict,
            FACTORY_CLASS=shelter_factory,
            owner=my_shelter.owner,
            email=fake.email()
        )

        payload['owner'] = payload['owner'].id
        data = {'animal_types': [val.slug for val in my_types]}

        payload.update(data)
        request = rf.post(
            endpoint,
            content_type='application/json',
            data=json.dumps(payload),
        )
        request.user = my_shelter.owner

        serializer = ShelterSerializer(data=payload,
                                       context={'request': request})
        assert not serializer.is_valid()

        request.user = user_factory.create(status='moderator')
        serializer = ShelterSerializer(data=payload,
                                       context={'request': request})
        assert not serializer.is_valid()

        request.user = user
        serializer = ShelterSerializer(data=payload,
                                       context={'request': request})
        assert serializer.is_valid()

    def test_gallery_image_validator(self):
        validator = ImageValidator()

        target_size = MAX_IMAGE_SIZE + 1
        bytes_data = get_image_data(target_size)

        big_image = SimpleUploadedFile(name='test_image.jpg',
                                       content=bytes_data)
        data = {'image': big_image}

        with pytest.raises(ValidationError):
            validator(data)

        target_size = 1000
        bytes_data = get_image_data(target_size)

        small_image = SimpleUploadedFile(name='test_image.jpg',
                                         content=bytes_data)
        data = {'image': small_image}

        assert validator(data) is None

    def test_email_serializer(self, client, new_user_data):
        url_signup = '/api/auth/users/'
        request = client.post(url_signup, new_user_data)

        payload = {
            'email': new_user_data.get('email')
        }

        serializer = EmailSerializer(data=payload,
                                     context={'request': request})

        assert not serializer.is_valid()

        payload = {
            'email': 'other_user@helppaw.fake'
        }

        serializer = EmailSerializer(data=payload,
                                     context={'request': request})
        assert serializer.is_valid()

    def test_article_validate(self, news_factory):
        image_data = {
            'image': base64.b64encode(get_image_data()).decode('utf-8')
        }

        payload = factory.build(
            dict,
            FACTORY_CLASS=news_factory,
            gallery=[image_data] * (MAX_IMAGE_CNT + 1)
        )

        serializer = NewsSerializer()
        with pytest.raises(ValidationError):
            serializer.validate(payload)

    @pytest.mark.parametrize('ftype', ['help-articles', 'news'])
    def test_article_update_clear_gallery(self, ftype, news_factory,
                                          help_article_factory,
                                          gallery_factory
                                          ):
        serializer = (
            NewsSerializer if ftype == 'news' else HelpArticleSerializer)
        my_factory = (
            news_factory if ftype == 'news' else help_article_factory)
        my_gallery = gallery_factory.create_batch(3)
        my_obj = my_factory.create(gallery=my_gallery)

        assert my_obj.gallery.count() == 3
        image_data = {
            'image': base64.b64encode(get_image_data()).decode('utf-8')
        }

        payload = factory.build(
            dict,
            FACTORY_CLASS=news_factory,
            gallery=[image_data] * MAX_IMAGE_CNT
        )

        my_serializer = serializer(my_obj, data=payload, partial=True)
        assert my_serializer.is_valid()

        my_serializer.save()

        assert my_obj.gallery.count() == MAX_IMAGE_CNT
