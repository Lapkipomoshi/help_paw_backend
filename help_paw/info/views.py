from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsAdminModerOrReadOnly, IsShelterOwner
from info.models import FAQ, HelpArticle, News, Vacancy
from info.serializers import (FAQSerializer, HelpArticleSerializer,
                              HelpArticleShortSerializer, NewsSerializer,
                              NewsShortSerializer, VacancySerializer)
from shelters.models import Shelter


class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminModerOrReadOnly, ]

    def perform_create(self, serializer):
        if isinstance(self, NewsViewSet):
            serializer.save(on_main=True)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        for image in instance.gallery.all():
            if isinstance(self, HelpArticleViewSet):
                objects = image.helparticle_related.all()
            elif isinstance(self, NewsViewSet):
                objects = image.news_related.all()
            else:
                raise NotImplementedError('Неподдерживаемый вьюсет')

            if len(objects) == 1 and objects[0] == instance:
                image.delete()
        instance.delete()


class NewsViewSet(ArticleViewSet):
    """Новости приютов."""
    search_fields = ('header',)

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


class HelpArticleViewSet(ArticleViewSet):
    """Полезные статьи."""
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


class FAQViewSet(viewsets.ModelViewSet):
    """Ответы на часто задаваемые вопросы."""
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = (IsAdminModerOrReadOnly,)
