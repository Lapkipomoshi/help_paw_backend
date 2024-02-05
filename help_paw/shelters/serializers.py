import datetime as dt

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from gallery.serializers import ImageSerializer, ImageValidator
from shelters.models import AnimalType, Pet, Shelter


class AnimalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = AnimalType


class ShelterNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name',)
        model = Shelter


class ShelterShortSerializer(serializers.ModelSerializer):
    working_from_hour = serializers.TimeField(format='%H:%M')
    working_to_hour = serializers.TimeField(format='%H:%M')
    warning = serializers.SerializerMethodField(read_only=True)
    is_favourite = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'name', 'address', 'working_from_hour', 'working_to_hour',
            'logo', 'profile_image', 'long', 'lat', 'warning', 'web_site',
            'is_favourite',
        )
        model = Shelter

    # TODO Add logic when algorithm invented
    def get_warning(self, obj) -> str:
        return 'yellow'

    def get_is_favourite(self, obj) -> bool:
        user = self.context['request'].user
        return obj.subscribers.filter(id=user.id).exists()


class ShelterSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    logo = Base64ImageField(required=False, allow_null=True)
    profile_image = Base64ImageField(required=False, allow_null=True)
    animal_types = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=AnimalType.objects.all(),
        allow_empty=False
    )
    money_collected = serializers.SerializerMethodField(read_only=True)
    animals_adopted = serializers.SerializerMethodField(read_only=True)
    working_from_hour = serializers.TimeField(format='%H:%M')
    working_to_hour = serializers.TimeField(format='%H:%M')
    is_favourite = serializers.SerializerMethodField()
    count_vacancies = serializers.SerializerMethodField(read_only=True)
    count_pets = serializers.SerializerMethodField(read_only=True)
    count_news = serializers.SerializerMethodField(read_only=True)
    count_tasks = serializers.SerializerMethodField(read_only=True)
    is_partner = serializers.SerializerMethodField(read_only=True)

    class Meta:
        exclude = ('is_approved',)
        model = Shelter

    def get_money_collected(self, obj) -> float:
        return sum(obj.payments.values_list('amount', flat=True))

    def get_animals_adopted(self, obj) -> int:
        return obj.pets.filter(is_adopted=True).count()

    def get_count_vacancies(self, obj) -> int:
        return obj.vacancy.count()

    def get_count_pets(self, obj) -> int:
        return obj.pets.filter(is_adopted=False).count()

    def get_count_news(self, obj) -> int:
        return obj.news.count()

    def get_count_tasks(self, obj) -> int:
        return obj.tasks.count()

    def get_is_partner(self, obj) -> bool:
        return obj.yookassa_token.exists()

    def get_is_favourite(self, obj) -> bool:
        user = self.context['request'].user
        return obj.subscribers.filter(id=user.id).exists()

    def validate(self, attrs):
        if self.context['request'].method == 'POST':
            user = self.context['request'].user
            if Shelter.objects.filter(owner=user).exists():
                raise serializers.ValidationError(
                    'Пользователь может зарегистрировать только один приют')
            if not user.is_user:
                raise serializers.ValidationError(
                    'Администраторам и модераторам нельзя регистрировать приюты')
        return attrs


class PetSerializer(serializers.ModelSerializer):
    animal_type = serializers.SlugRelatedField(
        slug_field='slug', queryset=AnimalType.objects.all()
    )
    gallery = ImageSerializer(many=True, required=False,
                              validators=[ImageValidator()])
    is_adopted = serializers.BooleanField(read_only=True)
    birth_date = serializers.DateField(write_only=True)
    admission_date = serializers.DateField(required=True, write_only=True)
    age = serializers.SerializerMethodField(read_only=True)
    sheltering_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'animal_type', 'sex', 'birth_date', 'about',
            'shelter', 'gallery', 'is_adopted', 'breed', 'admission_date',
            'sheltering_time', 'age'
        )
        model = Pet

    def get_sheltering_time(self, obj) -> int:
        duration = dt.date.today() - obj.admission_date
        return int(duration.days / 365)

    def get_age(self, obj) -> int:
        duration = dt.date.today() - obj.birth_date
        return int(duration.days / 365)
