import json

import factory
import pytest
from api.serializers import HelpArticleSerializer, ShelterSerializer
from faker import Faker

fake = Faker()
pytestmark = pytest.mark.django_db(transaction=True)


class TestSerializers:

    def test_help_article_serializer(self, help_article_factory, rf):

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
