import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from faker import Faker
from shelters.models import Shelter

pytestmark = pytest.mark.django_db(transaction=True)
fake = Faker()
User = get_user_model()


class TestInfoModels:

    def test_news_str_method(self, news_factory):
        my_news = news_factory(header='test_header')

        assert my_news.__str__() == 'test_header'[:10]

    def test_help_str_method(self, help_article_factory):
        my_help_article = help_article_factory(header='test_header')

        assert my_help_article.__str__() == 'test_header'[:10]

    def test_faq_str_method(self, faq_factory):
        my_faq = faq_factory(question='test_question')

        assert my_faq.__str__() == 'test_question'

    def test_static_info_str_method(self, static_info_factory):
        my_static_info = static_info_factory(about_us='test_about_us')

        assert my_static_info.__str__() == 'test_about_us'

    def test_vacancy_str_method(self, vacancy_factory):
        my_vacancy = vacancy_factory(position='test_position')

        assert my_vacancy.__str__() == 'test_position'

    def test_schedule_str_method(self, schedule_factory):
        my_schedule = schedule_factory(names='test_schedule')

        assert my_schedule.__str__() == 'test_schedule'

    def test_education_str_method(self, education_factory):
        my_education = education_factory(name='test_education')

        assert my_education.__str__() == 'test_education'

class TestShelterModels:

    def test_animal_type_str_method(self, animal_type_factory):
        my_animal_type = animal_type_factory(name='test_animal_type')

        assert my_animal_type.__str__() == 'test_animal_type'

    def test_pet_str_method(self, pet_factory):
        my_pet = pet_factory(name='test_name')

        assert my_pet.__str__() == 'test_name'

    def test_task_str_method(self, task_factory):
        my_task = task_factory(name='test_name')

        assert my_task.__str__() == 'test_name'

    def test_shelter_str_method(self, shelter_factory):
        my_shelter = shelter_factory(name='test_name')

        assert my_shelter.__str__() == 'test_name'

    def test_shelter_approved_queryset(self, shelter_factory):
        """Тест кастомного менеджера модели ApprovedSheltersManager"""
        shelter_factory.create(is_approved=False)
        queryset = Shelter.approved.get_queryset()

        assert queryset.count() == 0

        shelter_factory.create()
        queryset = Shelter.approved.get_queryset()

        assert queryset.count() == 1

    def test_shelter_tin_validation(self, shelter_factory):
        """Тест валидатора ИНН"""
        with pytest.raises(ValidationError):
            my_shelter = shelter_factory.build(tin='must_fail')
            my_shelter.clean_fields()

    def test_shelter_phone_validation(self, shelter_factory):
        """Тест валидатора номера телефона"""
        with pytest.raises(ValidationError):
            my_shelter = shelter_factory.build(phone_number='must_fail')
            my_shelter.clean_fields()

    def test_shelter_delete(self, shelter_factory):
        """Тест удаления объекта, кастомный метод delete()."""

        my_shelter = shelter_factory.create()
        owner = my_shelter.owner
        status_before = owner.status

        assert status_before == User.SHELTER_OWNER

        my_shelter.delete()
        status_after = owner.status

        assert status_after == User.USER


class TestChatModels:

    def test_chat_str_method(self, chat_factory, shelter_factory,
                             user_factory):
        my_shelter = shelter_factory.create(name='test_name')
        my_user = user_factory.create(username='test_name')
        my_chat = chat_factory(shelter=my_shelter, user=my_user)

        assert my_chat.__str__() == 'test_name -> test_name'

    def test_message_str_method(self, message_factory):
        my_text = fake.text()
        my_message = message_factory(text=my_text)

        assert my_message.__str__() == my_text[:20]

    def test_chat_validation(self, chat_factory, shelter_factory):
        """Тест валидатора модели, кастомный метод clean()."""
        my_shelter = shelter_factory.create()
        with pytest.raises(ValidationError):
            my_chat = chat_factory.create(shelter=my_shelter,
                                          user=my_shelter.owner)
            my_chat.clean()


class TestUserModels:

    def test_user_str_method(self, user_factory):
        my_user = user_factory(username='test_username')

        assert my_user.__str__() == 'test_username'

    def test_user_props(self, user_factory):
        """Тест свойств класса user"""
        my_user = user_factory.build()
        assert my_user.is_user

        my_admin = user_factory.build(status='admin')
        assert my_admin.is_admin

        my_moderator = user_factory.build(status='moderator')
        assert my_moderator.is_moderator

        my_shelter_owner = user_factory.build(status='shelter_owner')
        assert my_shelter_owner.is_shelter_owner

    def test_user_pet_str_method(self, pet_factory, user_factory,
                                 user_pet_factory):
        my_pet = pet_factory(name='test_name')
        my_pet_subscriber = user_factory(username='test_username')
        my_user_pet = user_pet_factory(pet=my_pet,
                                       pet_subscriber=my_pet_subscriber)

        assert my_user_pet.__str__() == (
            'test_username следит за судьбой: test_name')

    def test_user_shelter_str_method(self, user_factory, shelter_factory,
                                     user_shelter_factory):
        my_shelter_subscriber = user_factory(username='test_username')
        my_shelter = shelter_factory(name='test_name')

        my_user_shelter = user_shelter_factory(
            shelter_subscriber=my_shelter_subscriber, shelter=my_shelter)

        assert my_user_shelter.__str__() == (
            'test_username подписан на приют: test_name')
