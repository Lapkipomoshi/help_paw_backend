from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from geopy.geocoders import Nominatim
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from api.serializers import (AnimalTypeSerializer, FAQSerializer, HelpArticleSerializer,
                             HelpArticleShortSerializer, NewsSerializer,
                             NewsShortSerializer, PetSerializer,
                             ShelterSerializer, ShelterShortSerializer, VacancySerializer)
from info.models import FAQ, HelpArticle, News, Vacancy
from shelters.models import AnimalType, Pet, Shelter

from .filters import PetFilter, SheltersFilter
from .permissions import IsAdminModerOrReadOnly, IsOwnerAdminOrReadOnly


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

    @action(detail=False, methods=('get', ), url_path='on-main')
    def on_main(self, request):
        """Список приютов для главной страницы."""
        queryset = self.get_queryset().order_by('?')
        limit = request.query_params.get('limit', default='0')
        if limit != '0' and limit.isdigit():
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        data = ShelterShortSerializer(queryset, many=True)
        return Response(data.data)

    @staticmethod
    def get_coordinates(address: str) -> tuple[float, float]:
        """Получение координат адреса через GeoPy."""
        try:
            geolocator = Nominatim(user_agent='help_paw')
            location = geolocator.geocode(address)
            long, lat = location.longitude, location.latitude
        except Exception:
            long, lat = None, None
        return long, lat

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'user': self.request.user}
        )
        serializer.is_valid(raise_exception=True)
        owner = self.request.user
        address = serializer.validated_data.get('address')
        if address:
            long, lat = self.get_coordinates(address)
        else:
            long, lat = None, None
        shelter = serializer.save(owner=owner, long=long, lat=lat)
        response = ShelterSerializer(shelter)
        headers = self.get_success_headers(response.data)
        return Response(
            response.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        instance = self.get_object()
        address = serializer.validated_data.get('address')
        if address:
            long, lat = self.get_coordinates(address)
        else:
            long, lat = instance.long, instance.lat
        serializer.save(long=long, lat=lat, partial=True)


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
    queryset = Vacancy.objects.filter(is_closed=False)
    serializer_class = VacancySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('shelter',)


class AnimalTypeViewSet(viewsets.ModelViewSet):
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('shelters',)
