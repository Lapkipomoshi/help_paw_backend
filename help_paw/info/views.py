from api.permissions import IsAdminModerOrReadOnly, IsShelterOwner
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from shelters.models import Shelter

from info.models import HelpArticle, News, Vacancy
from info.serializers import (HelpArticleSerializer,
                              HelpArticleShortSerializer, NewsSerializer,
                              NewsShortSerializer, VacancySerializer)


class NewsViewSet(viewsets.ModelViewSet):
    """Новости приютов."""
    search_fields = ('header',)
    permission_classes = [IsAdminModerOrReadOnly, ]

    def get_queryset(self):
        shelter_id = self.kwargs.get('shelter_id')
        filter_kwargs = {'shelter': shelter_id} if shelter_id else {
            'on_main': True}

        if self.action == 'list':
            return News.objects.filter(**filter_kwargs).select_related(
                'shelter').only(
                'id', 'pub_date', 'profile_image', 'header', 'shelter__name'
            )
        else:
            return News.objects.filter(**filter_kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return NewsShortSerializer
        else:
            return NewsSerializer

    def perform_create(self, serializer):
        serializer.save(on_main=True)

    def perform_destroy(self, instance):
        for image in instance.gallery.all():
            news = image.news_related.all()
            if len(news) == 1 and news[0] == instance:
                image.delete()
        instance.delete()


class MyShelterNewsViewSet(NewsViewSet):
    permission_classes = (IsAuthenticated and IsShelterOwner,)

    def get_queryset(self):
        shelter = self.request.user.shelter
        return News.objects.filter(shelter=shelter)

    def perform_create(self, serializer):
        shelter = self.request.user.shelter
        serializer.save(shelter=shelter)


class VacancyViewSet(viewsets.ModelViewSet):
    serializer_class = VacancySerializer
    permission_classes = [IsAdminModerOrReadOnly, ]

    def get_queryset(self):
        shelter_id = self.kwargs.get('shelter_id')
        if shelter_id:
            shelter = get_object_or_404(Shelter, id=shelter_id)
            return Vacancy.objects.filter(shelter=shelter, is_closed=False)
        return Vacancy.objects.filter(shelter=None, is_closed=False)

    @action(detail=True, methods=('patch',), url_path='toggle-close')
    def toggle_close(self, request, pk):
        vacancy = get_object_or_404(Vacancy, id=pk)
        vacancy.is_closed = not vacancy.is_closed
        vacancy.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyShelterVacancyViewSet(VacancyViewSet):
    permission_classes = (IsShelterOwner,)

    def get_queryset(self):
        shelter = self.request.user.shelter
        return Vacancy.objects.filter(shelter=shelter)

    def perform_create(self, serializer):
        shelter = self.request.user.shelter
        serializer.save(shelter=shelter)


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

    def perform_destroy(self, instance):
        for image in instance.gallery.all():
            help_articles = image.helparticle_related.all()
            if len(help_articles) == 1 and help_articles[0] == instance:
                image.delete()
        instance.delete()
