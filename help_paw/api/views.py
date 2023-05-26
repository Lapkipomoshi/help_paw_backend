from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.compat import get_user_email
from djoser.email import ActivationEmail
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from api.serializers import (AnimalTypeSerializer, FAQSerializer,
                             HelpArticleSerializer, HelpArticleShortSerializer,
                             PetSerializer, ShelterSerializer,
                             ShelterShortSerializer, VacancySerializer)
from chat.models import Chat
from chat.serializers import ChatSerializer
from help_paw.settings import DJOSER
from info.models import FAQ, HelpArticle, Vacancy
from shelters.models import AnimalType, Pet, Shelter

from .filters import PetFilter, SheltersFilter
from .permissions import (IsAdminModerOrReadOnly, IsOwnerAdminOrReadOnly,
                          IsShelterOwnerOrAdmin)

User = get_user_model()


class FAQViewSet(viewsets.ModelViewSet):
    """Ответы на часто задаваемые вопросы."""
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    filter_backends = (SearchFilter,)
    permission_classes = (IsAdminModerOrReadOnly,)


class HelpArticleViewSet(viewsets.ModelViewSet):
    """Полезные статьи."""
    permission_classes = [IsAdminModerOrReadOnly, ]

    def get_queryset(self):
        if self.action == 'list':
            return HelpArticle.objects.only('id', 'header', 'profile_image')
        else:
            return HelpArticle.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return HelpArticleShortSerializer
        else:
            return HelpArticleSerializer


class ShelterViewSet(viewsets.ModelViewSet):
    """Приюты."""
    filter_backends = [DjangoFilterBackend, SearchFilter, ]
    filterset_class = SheltersFilter
    search_fields = ('name', )
    permission_classes = [IsOwnerAdminOrReadOnly, ]

    def get_queryset(self, *args, **kwargs):
        if self.action in ('list', 'on_main',):
            return Shelter.approved.only(
                'id', 'name', 'address', 'working_from_hour',
                'working_to_hour', 'logo', 'profile_image', 'long', 'lat'
            )
        else:
            return Shelter.approved.all()

    def get_serializer_class(self):
        if self.action in ('list', 'on_main', ):
            return ShelterShortSerializer
        if self.action == 'start_chat':
            return ChatSerializer
        else:
            return ShelterSerializer

    @action(detail=False, methods=('get',), url_path='on-main')
    def on_main(self, request):
        """Список приютов для главной страницы."""
        queryset = self.get_queryset().order_by('?')
        return super().list(queryset)

    @action(detail=True, methods=('post',), url_path='start-chat')
    def start_chat(self, request, pk):
        shelter = get_object_or_404(Shelter, id=pk)
        chat = Chat.objects.get_or_create(shelter=shelter, user=request.user)
        serializer = self.get_serializer(chat[0])
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(owner=user)


class PetViewSet(viewsets.ModelViewSet):
    """Питомцы."""
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_class = PetFilter
    search_fields = ('name', )
    permission_classes = (IsOwnerAdminOrReadOnly, )

    @action(detail=True, methods=('patch', ))
    def adopt(self, request, pk):
        """Изменяет булево значение поля is_adopted модели Pet
        на противоположное."""
        pet = get_object_or_404(Pet, id=pk)
        pet.is_adopted = not pet.is_adopted
        pet.save()
        serializer = self.get_serializer(pet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VacancyViewSet(viewsets.ModelViewSet):
    serializer_class = VacancySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('shelter',)
    permission_classes = (IsShelterOwnerOrAdmin,)

    def get_queryset(self):
        if self.action == 'own_vacancies':
            return Vacancy.objects.filter(shelter=None, is_closed=False)
        return Vacancy.objects.filter(is_closed=False)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_shelter_owner:
            serializer.save(shelter=user.shelter)
        serializer.save()

    @action(detail=False, methods=('get',), url_path='own-vacancies')
    def own_vacancies(self, request):
        queryset = self.get_queryset()
        return super().list(queryset)


class AnimalTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminModerOrReadOnly,)
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('shelters',)


class CustomUserViewSet(UserViewSet):
    def perform_update(self, serializer):
        initial_email = serializer.instance.email
        serializer.save(raise_exception=True)
        user = serializer.instance
        if DJOSER.get('SEND_ACTIVATION_EMAIL') and user.email != initial_email:
            context = {"user": user}
            to = [get_user_email(user)]
            ActivationEmail(self.request, context).send(to)
