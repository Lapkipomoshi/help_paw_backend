import json

import factory
import pytest
from faker import Faker
from info.serializers import HelpArticleSerializer
from shelters.serializers import ShelterSerializer
from users.serializers import EmailSerializer
from gallery.models import MAX_IMAGE_SIZE
from django.core.files.uploadedfile import SimpleUploadedFile
from tests.plugins.methods import get_image_data
from rest_framework.exceptions import ValidationError
from gallery.serializers import ImageValidator

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

    @pytest.mark.skip
    def test_email_reset_confirm_serializer(self):
        pass
