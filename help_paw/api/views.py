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
                             NewsSerializer, NewsShortSerializer,
                             PetSerializer, ShelterSerializer,
                             ShelterShortSerializer, VacancySerializer)
from help_paw.settings import DJOSER
from info.models import FAQ, HelpArticle, News, Vacancy
from shelters.models import AnimalType, Pet, Shelter

from .filters import PetFilter, SheltersFilter
from .permissions import (IsAdminModerOrReadOnly, IsOwnerAdminOrReadOnly,
                          IsShelterOwnerOrAdmin)

User = get_user_model()


class NewsViewSet(viewsets.ModelViewSet):
    """Новости приютов."""
    filter_backends = [DjangoFilterBackend, SearchFilter, ]
    filterset_fields = ('shelter', 'on_main',)
    search_fields = ('header',)
    permission_classes = [IsAdminModerOrReadOnly, ]

    def get_queryset(self):
        if self.action == 'list':
            return News.objects.select_related('shelter').only(
                'id', 'pub_date', 'profile_image', 'header', 'shelter__name'
            )
        else:
            return News.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return NewsShortSerializer
        else:
            return NewsSerializer


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
        else:
            return ShelterSerializer

    @action(detail=False, methods=('get',), url_path='on-main')
    def on_main(self, request):
        """Список приютов для главной страницы."""
        queryset = self.get_queryset().order_by('?')
        limit = request.query_params.get('limit', default='0')
        if limit != '0' and limit.isdigit():
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        data = self.get_serializer(queryset, many=True)
        return Response(data.data)

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
        limit = request.query_params.get('limit', default='0')
        if limit != '0' and limit.isdigit():
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        data = self.get_serializer(queryset, many=True)
        return Response(data.data)


class AnimalTypeViewSet(viewsets.ModelViewSet):
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
