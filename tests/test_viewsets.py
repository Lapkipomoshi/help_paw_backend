import json

import factory
import pytest
from api.serializers import (HelpArticleSerializer, HelpArticleShortSerializer,
                             ShelterSerializer, ShelterShortSerializer,
                             VacancySerializer)
from api.views import ShelterViewSet, VacancyViewSet
from chat.models import Chat
from chat.serializers import (ChatListSerializer, ChatSerializer,
                              MessageSerializer)
from chat.views import MessageViewSet
from faker import Faker
from info.models import Vacancy
from rest_framework.test import force_authenticate
from shelters.models import Pet, Shelter

fake = Faker()
pytestmark = pytest.mark.django_db(transaction=True)


class TestChatViewSets:
    endpoint = '/api/v1/chats/'

    def test_chat_get_queryset(self, api_client, user, chat_factory):
        chat_factory.create_batch(10)

        api_client.force_authenticate(user=user)
        response = api_client.get(self.endpoint)

        assert len(response.data) == 0

        chat_factory.create(user=user)
        response = api_client.get(self.endpoint)

        assert len(response.data) == 1

    def test_chat_get_serializer_class(self, api_client, user,
                                       chat_factory):
        api_client.force_authenticate(user=user)
        response = api_client.get(self.endpoint)

        assert response.status_code == 200
        assert isinstance(response.data.serializer.child, ChatListSerializer)

        my_chat = chat_factory.create(user=user)
        payload = {
            'text': fake.text()
        }
        response = api_client.post(
            self.endpoint + f'{my_chat.pk}/send-message/', payload)

        assert response.status_code == 201
        assert isinstance(response.data.serializer, MessageSerializer)

        response = api_client.get(self.endpoint + f'{my_chat.pk}/')

        assert response.status_code == 200
        assert isinstance(response.data.serializer, ChatSerializer)

    def test_message_get_queryset(self, rf, api_client, user, chat_factory,
                              message_factory):
        other_chat = chat_factory.create()
        message_factory.create(chat=other_chat)

        my_chat = chat_factory.create(user=user)
        my_message = message_factory.create(chat=my_chat)

        url = self.endpoint + f'{my_chat.pk}/messages/{my_message.pk}/'
        request = rf.get(url)
        view = MessageViewSet()
        view.request = request
        view.kwargs = {'chat_id': my_chat.id}

        queryset = view.get_queryset()

        assert len(queryset) == 1

    def test_message_update(self, rf, api_client, message_factory):
        my_message = message_factory.create()
        api_client.force_authenticate(user=my_message.author)

        assert not my_message.is_edited

        payload = {
            'text': fake.text()
        }
        response = api_client.patch(
            self.endpoint + f'{my_message.chat.pk}'
                            f'/messages/{my_message.pk}/', payload)

        assert response.status_code == 200
        assert response.data.get('is_edited')

    def test_shelter_chat_get_queryset(self, api_client, chat_factory):
        endpoint = '/api/v1/my-shelter/chats/'
        chat_factory.create_batch(3)
        my_chat = chat_factory.create()
        api_client.force_authenticate(user=my_chat.shelter.owner)
        response = api_client.get(endpoint)

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1


class TestAPIViewSets:
    endpoint = '/api/v1/'

    def test_news_get_queryset(self, api_client, news_factory):
        news_factory.create_batch(9)
        my_news = news_factory.create()

        fields = ['id', 'pub_date', 'profile_image', 'header', 'shelter']
        extra_fields = ['image_1', 'image_2', 'image_3', 'text']

        response = api_client.get(self.endpoint + 'news/')

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 10

        response_json = response.json()

        for field in fields:
            assert field in response_json[0]

        for field in extra_fields:
            assert field not in response_json[0]

        response = api_client.get(self.endpoint + f'news/{my_news.pk}/')

        assert response.status_code == 200

        response_json = response.json()

        all_fields = fields + extra_fields
        for field in all_fields:
            assert field in response_json

    def test_help_article_get_queryset_get_serializer(self, api_client,
                                                      help_article_factory):
        help_article_factory.create_batch(9)
        my_help = help_article_factory.create()

        fields = ['id', 'header', 'profile_image']
        extra_fields = ['pub_date', 'text', 'source']

        response = api_client.get(self.endpoint + 'help-articles/')

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 10
        assert isinstance(response.data.serializer.child,
                          HelpArticleShortSerializer)

        response_json = response.json()

        for field in fields:
            assert field in response_json[0]

        for field in extra_fields:
            assert field not in response_json[0]

        response = api_client.get(
            self.endpoint + f'help-articles/{my_help.pk}/')

        assert response.status_code == 200
        assert isinstance(response.data.serializer, HelpArticleSerializer)

        response_json = response.json()

        all_fields = fields + extra_fields
        for field in all_fields:
            assert field in response_json

    def test_shelter_get_queryset_get_serializer(self, api_client,
                                                 shelter_factory):
        endpoints = [self.endpoint + 'shelters/',
                     self.endpoint + 'shelters/on-main/']

        shelter_factory.create(is_approved=False)

        for my_endpoint in endpoints:
            response = api_client.get(my_endpoint)
            assert len(json.loads(response.content)) == 0

        my_shelter = shelter_factory.create()

        fields = ['id', 'name', 'address', 'working_from_hour',
                  'working_to_hour', 'logo', 'profile_image', 'long', 'lat']
        extra_fields = ['owner', 'legal_owner_name', 'tin',
                        'description', 'animal_types', 'phone_number', 'email',
                        'web_site', 'vk_page', 'ok_page', 'telegram']

        for my_endpoint in endpoints:

            response = api_client.get(my_endpoint)
            assert response.status_code == 200
            assert len(json.loads(response.content)) == 1
            assert isinstance(response.data.serializer.child,
                              ShelterShortSerializer)

            response_json = response.json()
            for field in fields:
                assert field in response_json[0]

            for field in extra_fields:
                assert field not in response_json[0]

        response = api_client.get(self.endpoint + f'shelters/{my_shelter.pk}/')

        assert response.status_code == 200
        assert isinstance(response.data.serializer, ShelterSerializer)

        response_json = response.json()

        all_fields = fields + extra_fields
        for field in all_fields:
            assert field in response_json

        chat_fields = ['id', 'shelter', 'user', 'messages']
        api_client.force_authenticate(user=my_shelter.owner)
        response = api_client.post(
            self.endpoint + f'shelters/{my_shelter.pk}/start-chat/')
        qs_after = Chat.objects.all()

        assert response.status_code == 200
        assert qs_after.count() == 1
        assert isinstance(response.data.serializer, ChatSerializer)

        response_json = response.json()

        for field in chat_fields:
            assert field in response_json

    def test_shelter_create(self, rf, user, user_factory, shelter_factory,
                            animal_type_factory):
        url = self.endpoint + f'shelters/'
        my_types = animal_type_factory.create_batch(3)
        payload = factory.build(
            dict,
            FACTORY_CLASS=shelter_factory,
            owner=user
        )
        my_shelter = Shelter.objects.create(**payload)
        owner_before = my_shelter.owner

        data = {'animal_types': [v.slug for v in my_types]}
        payload.update(data)
        payload.pop('owner')

        request = rf.post(
            url,
            content_type='application/json',
            data=json.dumps(payload),
        )
        request.user = user_factory.create()  # подменяю юзера

        serializer = ShelterSerializer(instance=my_shelter,
                                       data=data,
                                       partial=True,
                                       context={'request': request})

        assert serializer.is_valid()

        serializer.save()
        view = ShelterViewSet(request=request)
        view.perform_create(serializer)

        assert owner_before != my_shelter.owner

    def test_pet_adopt(self, user, api_client, pet_factory, shelter_factory):
        my_shelter = shelter_factory(owner=user)
        my_pet = pet_factory.create(shelter=my_shelter, is_adopted=False)
        my_pet_pk = my_pet.pk

        api_client.force_authenticate(user=user)
        response = api_client.patch(
            self.endpoint + f'pets/{my_pet_pk}/adopt/')

        assert response.status_code == 200
        assert response.data.get('is_adopted')

        reread_pet = Pet.objects.get(pk=my_pet_pk)

        assert reread_pet.is_adopted

    def test_vacancy_get_queryset(self, vacancy_factory, api_client):
        vacancy_factory.create(shelter=None)
        vacancy_factory.create(is_closed=True)
        vacancy_factory.create()

        response = api_client.get(self.endpoint + 'vacancies/')

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 2

        response = api_client.get(self.endpoint + 'vacancies/own-vacancies/')

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1

    def test_vacancy_create(self, rf, user, vacancy_factory, shelter_factory):
        shelter = shelter_factory.create(owner=user)

        url = self.endpoint + f'vacancies/'
        payload = factory.build(
            dict,
            FACTORY_CLASS=vacancy_factory,
            shelter=None,
        )

        request = rf.post(
            url,
            content_type='application/json',
            data=json.dumps(payload),
        )

        force_authenticate(request, user=user)

        request.user = user
        view = VacancyViewSet()
        view.request = request

        serializer = VacancySerializer(data=payload,
                                       context={'request': request})
        assert serializer.is_valid()
        serializer.save()

        view = VacancyViewSet(request=request)
        view.perform_create(serializer)

        my_vac = Vacancy.objects.get(pk=serializer.data.get('id'))
        assert my_vac.shelter == shelter
