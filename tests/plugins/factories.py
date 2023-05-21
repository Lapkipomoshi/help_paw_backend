import factory
from chat.models import Chat, Message
from faker import Faker
from info.models import FAQ, HelpArticle, News, StaticInfo, Vacancy
from shelters.models import AnimalType, Pet, Shelter, Task
from users.models import User, UserPet, UserShelter

fake = Faker()

TIN_MIN_VAL = 1000000000
TIN_MAX_VAL = 9999999999
PHONE_NUM = '+12345678910'


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = fake.name()
    email = factory.Sequence(lambda n: f'person{n}@helppaw.com')
    password = fake.password()
    status = 'user'


class AnimalTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AnimalType

    name = fake.name()
    slug = fake.slug()


class ShelterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shelter

    is_approved = True
    owner = factory.SubFactory(UserFactory)
    legal_owner_name = fake.name()
    tin = factory.Sequence(lambda n: n + fake.pyint(min_value=TIN_MIN_VAL,
                                                    max_value=TIN_MAX_VAL))
    name = factory.Sequence(lambda n: fake.word() + f' #{n}'.capitalize())
    description = fake.text()
    address = fake.address()
    phone_number = PHONE_NUM
    working_from_hour = fake.time()
    working_to_hour = fake.time()
    email = factory.SelfAttribute('owner.email')


class PetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pet

    name = fake.name()
    animal_type = factory.SubFactory(AnimalTypeFactory)
    sex = 'other'
    birth_date = fake.date()
    about = fake.text()
    is_adopted = fake.boolean()
    shelter = factory.SubFactory(ShelterFactory)


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    shelter = factory.SubFactory(ShelterFactory)
    name = fake.name()
    description = fake.text()


class NewsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = News

    header = fake.words()
    shelter = factory.SubFactory(ShelterFactory)


class HelpArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HelpArticle

    header = fake.words()


class FAQFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FAQ

    question = fake.sentence()


class StaticInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StaticInfo

    about_us = fake.sentence()


class VacancyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vacancy

    position = fake.word()


class ChatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Chat

    shelter = factory.SubFactory(ShelterFactory)
    user = factory.SubFactory(UserFactory)


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    author = factory.SubFactory(UserFactory)
    chat = factory.SubFactory(ChatFactory)
    text = fake.text()
    is_readed = False
    is_edited = False


class UserPetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserPet

    pet_subscriber = factory.SubFactory(UserFactory)
    pet = factory.SubFactory(PetFactory)


class UserShelterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserShelter

    shelter_subscriber = factory.SubFactory(UserFactory)
    shelter = factory.SubFactory(ShelterFactory)
