from django_filters.rest_framework import DjangoFilterBackend
from geopy.geocoders import Nominatim
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api.serializers import (FAQSerializer, HelpArticleSerializer,
                             HelpArticleShortSerializer, NewsSerializer,
                             ShelterSerializer, ShelterShortSerializer)
from info.models import FAQ, HelpArticle, News
from shelters.models import Shelter

from .filters import SheltersFilter
from .permissions import IsAdminModerOrReadOnly, IsOwnerAdminOrReadOnly


class NewsViewSet(viewsets.ModelViewSet):
    """Новости приютов"""
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('header',)


class FAQViewSet(viewsets.ModelViewSet):
    """Ответы на часто задаваемые вопросы"""
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    filter_backends = (SearchFilter,)


class HelpArticleViewSet(viewsets.ModelViewSet):
    """Полезные статьи"""
    pagination_class = LimitOffsetPagination
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
    """Приюты"""
    filter_backends = [DjangoFilterBackend, SearchFilter, ]
    filterset_class = SheltersFilter
    search_fields = ('name', )
    pagination_class = LimitOffsetPagination
    permission_classes = [IsOwnerAdminOrReadOnly, ]

    def get_queryset(self, *args, **kwargs):
        if self.action in ('list', 'on_main', ):
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
        """Список приютов для главной страницы"""
        queryset = self.get_queryset().order_by('?')
        if request.query_params.get('limit'):
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            data = ShelterShortSerializer(queryset, many=True)
            return Response(data.data, status=status.HTTP_200_OK)

    @staticmethod
    def get_coordinates(address: str) -> tuple[float, float]:
        """Получение координат адреса через GeoPy"""
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
