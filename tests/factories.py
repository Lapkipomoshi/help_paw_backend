import factory
from faker import Faker

from shelters.models import Shelter, Pet, Task, AnimalType
from users.models import User, UserPet, UserShelter
from info.models import News, HelpArticle, FAQ, StaticInfo, Vacancy
from chat.models import Chat, Message

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = fake.name()
    email = fake.email()
    password = fake.password()
    status = 'user',


class AnimalTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AnimalType

    name = 'test_animal_type'
    slug = fake.slug()


class ShelterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shelter

    is_approved = True
    owner = factory.SubFactory(UserFactory)
    legal_owner_name = fake.name()
    tin = fake.pyint(min_value=10, max_value=10)
    name = 'test_name'
    description = fake.pystr()
    address = fake.address()
    phone_number = fake.phone_number()
    working_from_hour = fake.time()
    working_to_hour = fake.time()


class PetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pet

    name = 'test_name'
    animal_type = factory.SubFactory(AnimalTypeFactory)
    sex = 'other'
    birth_date = fake.date()
    about = fake.pystr()
    is_adopted = fake.boolean()
    shelter = factory.SubFactory(ShelterFactory)


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    shelter = factory.SubFactory(ShelterFactory)
    name = 'test_name'
    description = fake.pystr()


class NewsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = News

    header = 'test_header'
    shelter = factory.SubFactory(ShelterFactory)


class HelpArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HelpArticle

    header = 'test_header'


class FAQFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FAQ

    question = 'test_question'


class StaticInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StaticInfo

    about_us = 'test_about_us'


class VacancyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vacancy

    position = 'test_position'










