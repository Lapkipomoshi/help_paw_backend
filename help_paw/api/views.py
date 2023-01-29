from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from api.serializers import (FAQSerializer, HelpArticleSerializer,
                             HelpArticleShortSerializer, NewsSerializer,
                             ShelterSerializer, ShelterShortSerializer,
                             ShelterWriteSerializer)
from info.models import FAQ, HelpArticle, News
from shelters.models import Shelter

from .filters import SheltersFilter


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
    def get_queryset(self):
        if self.action == 'list':
            return HelpArticle.objects.only('header', 'profile_image')
        else:
            return HelpArticle.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return HelpArticleShortSerializer
        else:
            return HelpArticleSerializer


class ShelterViewSet(viewsets.ModelViewSet):
    def get_queryset(self, *args, **kwargs):
        if self.action == 'list':
            return Shelter.approved.only(
                'name', 'address', 'working_hours', 'logo', 'profile_image',
                'long', 'lat'
            )
        else:
            return Shelter.approved.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ShelterShortSerializer
        elif self.action == 'retrieve':
            return ShelterSerializer
        else:
            return ShelterWriteSerializer

    filter_backends = [DjangoFilterBackend, ]
    filterset_class = SheltersFilter

    @action(detail=False, methods=('get', ))
    def on_main(self, request):
        queriset = Shelter.approved.all().order_by('?')[:3]
        response = ShelterShortSerializer(queriset, many=True)
        return Response(response.data)
