import json

import factory
import pytest
from chat.models import Chat
from chat.serializers import (ChatListSerializer, ChatSerializer,
                              MessageSerializer)
from chat.views import MessageViewSet
from faker import Faker
from info.models import News, Vacancy
from info.serializers import (HelpArticleSerializer,
                              HelpArticleShortSerializer, NewsSerializer,
                              NewsShortSerializer, VacancyReadSerializer,
                              EducationSerializer, ScheduleSerializer)
from info.views import MyShelterNewsViewSet, NewsViewSet
from shelters.models import Pet, Shelter
from shelters.serializers import ShelterSerializer, ShelterShortSerializer
from shelters.views import ShelterViewSet

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

    def test_message_get_queryset(self, rf, user, chat_factory,
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

    def test_message_update(self, api_client, message_factory):
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


class TestSheltersViewSets:
    endpoint = '/api/v1/'

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
                  'working_to_hour', 'logo', 'profile_image', 'long', 'lat',
                  'warning', 'web_site', 'is_favourite']
        extra_fields = ['owner', 'legal_owner_name', 'tin',
                        'description', 'animal_types', 'phone_number', 'email',
                        'vk_page', 'ok_page', 'telegram', 'money_collected',
                        'animals_adopted', ]

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
        all_fields.remove('warning')

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

        data = {'animal_types': [val.slug for val in my_types]}
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

        api_client.force_authenticate(user=user)
        response = api_client.patch(
            self.endpoint + f'my-shelter/pets/{my_pet.pk}/adopt/')

        assert response.status_code == 200
        assert response.data.get('is_adopted')

        reread_pet = Pet.objects.get(pk=my_pet.pk)

        assert reread_pet.is_adopted

    def test_news_create(self, rf, news_factory, user):

        url = self.endpoint + f'news/'

        payload = factory.build(
            dict,
            FACTORY_CLASS=news_factory,
            on_main=False,
        )
        payload['shelter'] = payload['shelter'].id
        request = rf.post(
            url,
            content_type='application/json',
            data=json.dumps(payload),
        )

        request.user = user
        serializer = NewsSerializer(data=payload)

        assert serializer.is_valid()

        serializer.save()

        view = NewsViewSet(request=request)
        view.perform_create(serializer)

        news = News.objects.all()

        assert news.count() == 1 and news[0].on_main

    @pytest.mark.skip
    @pytest.mark.parametrize('url, count',
                             [('shelters/?warnings=red', 3),
                              ('shelters/?warnings=yellow', 2),
                              ('shelters/?warnings=green', 1)]
                             )
    def test_shelter_filters(self, url, count, task_factory, shelter_factory,
                             api_client):
        task_factory.create_batch(3, is_emergency=True)
        task_factory.create_batch(2)
        shelter_factory.create()

        response = api_client.get(self.endpoint + url)

        assert response.status_code == 200
        assert len(json.loads(response.content)) == count


class TestInfoViewSets:
    endpoint = '/api/v1/'
    fields = ['id', 'pub_date', 'profile_image', 'header', 'shelter']
    extra_fields = ['gallery', 'text']

    def test_news_get_queryset(self, api_client, news_factory):
        news_factory.create_batch(9, on_main=False)
        my_news = news_factory.create()

        fields = ['id', 'pub_date', 'profile_image', 'header', 'shelter']
        extra_fields = ['gallery', 'text']

        response = api_client.get(self.endpoint + 'news/')

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1

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

    def test_shelter_news_get_queryset_get_serializer(self, api_client,
                                                      shelter_factory,
                                                      news_factory):
        news_factory.create_batch(3)

        my_shelter = shelter_factory.create()
        my_news = news_factory.create(shelter=my_shelter)

        response = api_client.get(
            self.endpoint + f'shelters/{my_shelter.pk}/news/')

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1
        assert isinstance(response.data.serializer.child,
                          NewsShortSerializer)

        response_json = response.json()

        for field in self.fields:
            assert field in response_json[0]

        for field in self.extra_fields:
            assert field not in response_json[0]

        response = api_client.get(
            self.endpoint + f'shelters/{my_shelter.pk}/news/{my_news.pk}/')

        assert response.status_code == 200
        assert isinstance(response.data.serializer, NewsSerializer)

        response_json = response.json()

        all_fields = self.fields + self.extra_fields
        for field in all_fields:
            assert field in response_json

    def test_my_shelter_news_get_queryset_get_serializer(self, api_client,
                                                         shelter_factory,
                                                         news_factory):
        news_factory.create_batch(3)

        my_shelter = shelter_factory.create()

        news_factory.create_batch(2, shelter=my_shelter)
        api_client.force_authenticate(my_shelter.owner)

        response = api_client.get(self.endpoint + 'my-shelter/news/')

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 2
        assert isinstance(response.data.serializer.child,
                          NewsShortSerializer)

    def test_my_news_create(self, rf, news_factory, shelter_factory):

        shelter = shelter_factory.create()
        user = shelter.owner

        payload = factory.build(
            dict,
            FACTORY_CLASS=news_factory,
            shelter=None,
        )

        request = rf.post(
            self.endpoint,
            content_type='application/json',
            data=json.dumps(payload),
        )

        request.user = user
        serializer = NewsSerializer(data=payload)

        assert serializer.is_valid()

        serializer.save()

        view = MyShelterNewsViewSet(request=request)
        view.perform_create(serializer)

        news = News.objects.all()

        assert news.count() == 1 and news[0].shelter == shelter

    def test_vacancy_get_queryset(self, vacancy_factory, api_client,
                                  shelter_factory):
        my_shelter = shelter_factory.create()

        vacancy_factory.create()
        vacancy_factory.create(is_closed=True)
        vacancy_factory.create(shelter=None)
        vacancy_factory.create(shelter=None, is_closed=True)
        my_vacancy = vacancy_factory.create(shelter=my_shelter)
        vacancy_factory.create(shelter=my_shelter, is_closed=True)

        response = api_client.get(self.endpoint + 'vacancies/')

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1

        response = api_client.get(
            self.endpoint + f'shelters/{my_shelter.pk}/vacancies/')

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1
        assert response.json()[0].get('id') == my_vacancy.pk

    def test_vacancy_toggle_close(self, vacancy_factory, api_client, admin):

        my_vacancy = vacancy_factory.create(is_closed=False)
        api_client.force_authenticate(user=admin)
        response = api_client.patch(
            self.endpoint + f'vacancies/{my_vacancy.pk}/toggle-close/')

        assert response.status_code == 204

        vacancy = Vacancy.objects.get(pk=my_vacancy.pk)

        assert vacancy.is_closed != my_vacancy.is_closed

    def test_my_shelter_vacancy_get_queryset(self, vacancy_factory, api_client,
                                             shelter_factory):

        vacancy_factory.create_batch(3)
        my_shelter = shelter_factory.create()
        vacancy_factory.create(shelter=my_shelter)

        api_client.force_authenticate(user=my_shelter.owner)
        response = api_client.get(self.endpoint + 'my-shelter/vacancies/')

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1

    def test_my_shelter_vacancy_vacancy_create(self, rf, user, vacancy_factory,
                                               shelter_factory,
                                               education_factory,
                                               schedule_factory):
        shelter = shelter_factory.create(owner=user)

        education = EducationSerializer(education_factory.build())
        schedule = ScheduleSerializer(schedule_factory.build())

        url = self.endpoint + f'my-shelter/vacancies/'

        payload = factory.build(
            dict,
            FACTORY_CLASS=vacancy_factory,
            shelter=None,
            education=education.data,
            schedule=[schedule.data, ]
        )

        request = rf.post(
            url,
            content_type='application/json',
            data=json.dumps(payload),
        )
        request.user = user

        serializer = VacancyReadSerializer(data=payload,
                                           context={'request': request})
        assert serializer.is_valid()

        # FIXME
        # serializer.save()
        #
        # view = MyShelterVacancyViewSet(request=request)
        # view.perform_create(serializer)
        #
        # my_vac = Vacancy.objects.get(pk=serializer.data.get('id'))
        # assert my_vac.shelter == shelter
