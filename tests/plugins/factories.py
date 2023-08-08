import base64
from io import BytesIO

import factory
from chat.models import Chat, Message
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from info.models import (FAQ, Education, HelpArticle, News, Schedule,
                         StaticInfo, Vacancy)
from PIL import Image
from shelters.models import AnimalType, Pet, Shelter, Task
from users.models import User, UserPet, UserShelter

fake = Faker()

TIN_MIN_VAL = 1000000000
TIN_MAX_VAL = 9999999999
PHONE_NUM = '+12345678910'


def mock_image(file_name='example.jpg',
               width=100,
               height=100,
               image_format='JPEG',
               image_palette='RGB',
               color='blue',
               is_base64str=False):
    thumb_io = BytesIO()
    with Image.new(image_palette, (width, height), color) as thumb:
        thumb.save(thumb_io, format=image_format, filename=file_name)
    content = thumb_io.getvalue()

    some_image = SimpleUploadedFile(
        name=file_name,
        content=content,
        content_type="image/jpeg"
    )
    if is_base64str:
        return base64.b64encode(some_image.read()).decode()
    return some_image


def mock_base64str():
    thumb_io = BytesIO()
    thumb_io.write(b'test')
    content = thumb_io.getvalue()
    return base64.b64encode(content).decode()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: fake.name() + f' #{n}')
    email = factory.Sequence(lambda n: f'person{n}@helppaw.com')
    password = fake.password()
    status = 'user'


class AnimalTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AnimalType

    name = factory.Sequence(lambda n: fake.word().capitalize() + str(n))
    slug = factory.Sequence(lambda n: fake.slug() + str(n))


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

    @factory.post_generation
    def animal_types(self, create, extracted):
        if not create:
            return

        if extracted:
            for animal_type in extracted:
                self.animal_types.add(animal_type)


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
    # is_emergency = False
    # is_finished = False


class NewsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = News

    header = fake.word()
    text = fake.sentence()
    shelter = factory.SubFactory(ShelterFactory)
    on_main = True
    profile_image = ''


class HelpArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HelpArticle

    header = fake.words()
    text = fake.text()
    source = fake.url()
    profile_image = ''


class FAQFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FAQ

    question = fake.sentence()
    answer = fake.sentence()


class StaticInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StaticInfo

    about_us = fake.sentence()


class ScheduleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Schedule

    name = factory.Sequence(lambda n: "Schedule #%s" % n)
    slug = factory.Sequence(lambda n: fake.slug() + str(n))


class EducationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Education

    name = factory.Sequence(lambda n: "Education #%s" % n)
    slug = factory.Sequence(lambda n: fake.slug() + str(n))


class VacancyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vacancy

    shelter = factory.SubFactory(ShelterFactory)
    salary = fake.pyint()
    education = factory.SubFactory(EducationFactory)
    position = fake.word()
    description = fake.sentence()
    is_ndfl = 'ndfl'

    @factory.post_generation
    def schedule(self, create, extracted):
        if not create:
            return

        if extracted:
            for schedule in extracted:
                self.schedule.add(schedule)


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

    shelter_subscriber = factory.SubFactory(UserFactory,
                                            status='shelter_owner')
    shelter = factory.SubFactory(ShelterFactory)
