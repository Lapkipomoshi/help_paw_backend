import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from faker import Faker
from shelters.models import Shelter

from tests.plugins.factories import TIN_MAX_VAL, TIN_MIN_VAL

pytestmark = pytest.mark.django_db(transaction=True)
fake = Faker()
User = get_user_model()


# Тестирую:
# 1. дандер метод __str__ моделей
# 2. валидация полей моделей
# 3. методы по работе с моделями


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

    @pytest.mark.django_db(transaction=True)
    def test_shelter_approved_queryset(self, shelter_factory, user_factory):
        """Тест кастомного менеджера модели ApprovedSheltersManager"""
        shelter_factory.create(is_approved=False,
                               name=fake.name(),
                               owner=user_factory.create(
                                   email=fake.email()),
                               tin=fake.pyint(min_value=TIN_MIN_VAL,
                                              max_value=TIN_MAX_VAL))
        queryset = Shelter.approved.get_queryset()

        assert queryset.count() == 0

        shelter_factory.create(owner=user_factory.create(email=fake.email()),
                               name=fake.name(),
                               tin=fake.pyint(min_value=TIN_MIN_VAL,
                                              max_value=TIN_MAX_VAL))
        queryset = Shelter.approved.get_queryset()

        assert queryset.count() == 1

    @pytest.mark.django_db(transaction=True)
    def test_shelter_tin_validation(self, shelter_factory):
        """Тест валидатора ИНН"""
        with pytest.raises(ValidationError):
            my_shelter = shelter_factory.build(tin='must_fail')
            my_shelter.clean_fields()

    @pytest.mark.django_db(transaction=True)
    def test_shelter_phone_validation(self, shelter_factory):
        """Тест валидатора номера телефона"""
        with pytest.raises(ValidationError):
            my_shelter = shelter_factory.build(phone_number='must_fail')
            my_shelter.clean_fields()

    @pytest.mark.django_db(transaction=True)
    def test_shelter_validation(self, shelter_factory, user_factory):
        """Тест валидатора модели, кастомный метод clean()."""

        must_fail = user_factory.create(status='moderator', email=fake.email())
        with pytest.raises(ValidationError):
            my_shelter = shelter_factory.build(owner=must_fail)
            my_shelter.clean()

    @pytest.mark.django_db(transaction=True)
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
        my_user = user_factory.create(username='test_name',
                                      email=fake.email())
        my_chat = chat_factory(shelter=my_shelter, user=my_user)
        assert my_chat.__str__() == 'test_name -> test_name'

    def test_message_str_method(self, chat_factory, shelter_factory,
                                message_factory, user_factory):
        my_text = fake.text()
        my_shelter = shelter_factory.create()
        my_user = user_factory.create(email=fake.email())
        my_chat = chat_factory(shelter=my_shelter, user=my_user)
        my_message = message_factory(author=my_user, chat=my_chat,
                                     text=my_text)
        assert my_message.__str__() == my_text[:20]

    @pytest.mark.django_db(transaction=True)
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

    def test_user_pet_str_method(self, user_factory):
        pass

    def test_user_shelter_str_method(self, user_factory):
        pass
