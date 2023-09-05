from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.permissions import (AuthenticatedAllowToPost, IsAdminModerOrReadOnly,
                             IsShelterOwner)
from chat.models import Chat
from chat.serializers import ChatSerializer
from shelters.filters import PetFilter, SheltersFilter
from shelters.models import AnimalType, Pet, Shelter
from shelters.serializers import (AnimalTypeSerializer, PetSerializer,
                                  ShelterSerializer, ShelterShortSerializer)


class ShelterViewSet(viewsets.ModelViewSet):
    """Приюты. небезопасные методы доступны администратору/модератору,
     аутентифицированные пользователи могут создавать записи."""
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SheltersFilter
    search_fields = ('name',)
    permission_classes = (IsAdminModerOrReadOnly | AuthenticatedAllowToPost,)

    def get_queryset(self, *args, **kwargs):
        if self.action in ('list', 'on_main',):
            return Shelter.approved.only(
                'id', 'name', 'address', 'working_from_hour',
                'working_to_hour', 'logo', 'profile_image', 'long', 'lat'
            )
        else:
            return Shelter.approved.annotate(
                count_vacancies=Count('vacancy'),
                count_pets=Count('pets'),
                count_news=Count('news'),
                count_tasks=Count('tasks')
            )

    def get_serializer_class(self):
        if self.action in ('list', 'on_main',):
            return ShelterShortSerializer
        if self.action == 'start_chat':
            return ChatSerializer
        else:
            return ShelterSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(owner=user)

    @action(detail=False, methods=('get',), url_path='on-main')
    def on_main(self, request):
        """Список приютов для главной страницы."""
        queryset = self.get_queryset().order_by('?')
        return super().list(queryset)

    @action(detail=True, methods=('post',), url_path='start-chat')
    def start_chat(self, request, pk):
        """Создание чата с приютом, или получение уже имеющегося чата"""
        shelter = get_object_or_404(Shelter, id=pk)
        chat, _ = Chat.objects.get_or_create(shelter=shelter,
                                             user=request.user)
        serializer = self.get_serializer(chat)
        return Response(serializer.data)

    @action(detail=True, methods=('post', 'delete',), url_path='favourite',
            permission_classes=[IsAuthenticated])
    def toggle_is_favourite(self, request, pk):
        """Добавление/удаление приюта из избранного"""
        shelter = get_object_or_404(Shelter, id=pk)
        user = request.user
        if request.method == 'POST':
            user.subscription_shelter.add(shelter)
        if request.method == 'DELETE':
            user.subscription_shelter.remove(shelter)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyShelterViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Управление собственным приютом, доступно только для владельцев приюта."""
    permission_classes = (IsShelterOwner,)
    serializer_class = ShelterSerializer

    def get_object(self):
        return self.request.user.shelter

    def perform_destroy(self, instance):
        if instance.is_approved:
            instance.is_approved = False
            instance.save()
        else:
            super().perform_destroy(instance)


class PetViewSet(viewsets.ModelViewSet):
    """Питомцы.
    Небезопасные методы доступны только администратору/модератору."""
    serializer_class = PetSerializer
    permission_classes = (IsAdminModerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PetFilter

    def get_queryset(self):
        shelter_id = self.kwargs.get('shelter_id')
        if shelter_id:
            shelter = get_object_or_404(Shelter, id=shelter_id)
            return Pet.objects.filter(shelter=shelter, is_adopted=False)


class MyShelterPetViewSet(PetViewSet):
    """Управление питомцами собственного приюта,
    доступно только для владельцев приюта."""
    permission_classes = (IsShelterOwner,)

    def get_queryset(self):
        shelter = self.request.user.shelter
        return Pet.objects.filter(shelter=shelter)

    @action(detail=True, methods=('patch',), url_path='adopt')
    def toggle_adopt(self, request, pk):
        """Изменяет булево значение поля is_adopted модели Pet
        на противоположное."""
        pet = get_object_or_404(Pet, id=pk)
        pet.is_adopted = not pet.is_adopted
        pet.save()
        serializer = self.get_serializer(pet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnimalTypeViewSet(viewsets.ModelViewSet):
    """Виды животных.
    Небезопасные методы доступны только администратору/модератору."""
    permission_classes = (IsAdminModerOrReadOnly,)
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSerializer
