from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsAdminModerOrReadOnly, IsShelterOwner
from info.models import FAQ, Education, HelpArticle, News, Schedule, Vacancy
from info.serializers import (EducationSerializer, FAQSerializer,
                              HelpArticleSerializer,
                              HelpArticleShortSerializer, NewsSerializer,
                              NewsShortSerializer, ScheduleSerializer,
                              VacancyReadSerializer, VacancyWriteSerializer)
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
            else:
                objects = image.news_related.all()

            if len(objects) == 1 and objects[0] == instance:
                image.delete()
        instance.delete()


class NewsViewSet(ArticleViewSet):
    """Новости сайта, небезопасные методы доступны только
    администратору/модератору. Все созданные новости автоматически попадают
    на главную вкладку новостей."""
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
    """Полезные статьи, небезопасные методы доступны только
    администратору/модератору."""
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
    """Новости приюта, небезопасные методы доступны только
        владельцам приютов. Все созданные новости автоматически попадают
        на вкладку новостей приюта создателя."""
    permission_classes = (IsAuthenticated and IsShelterOwner,)

    def get_queryset(self):
        shelter = self.request.user.shelter
        return News.objects.filter(shelter=shelter)

    def perform_create(self, serializer):
        shelter = self.request.user.shelter
        serializer.save(shelter=shelter)


class VacancyViewSet(viewsets.ModelViewSet):
    """Вакансии, небезопасные методы доступны только
        администратору/модератору. Созданные вакансии попадают во вкладку
        вакансий сайта."""
    permission_classes = [IsAdminModerOrReadOnly, ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return VacancyReadSerializer
        return VacancyWriteSerializer

    def get_queryset(self):
        shelter_id = self.kwargs.get('shelter_id')
        if shelter_id:
            shelter = get_object_or_404(Shelter, id=shelter_id)
            return Vacancy.objects.filter(shelter=shelter, is_closed=False)
        return Vacancy.objects.filter(shelter=None, is_closed=False)

    @action(detail=True, methods=('patch',), url_path='toggle-close')
    def toggle_close(self, request, pk):
        """Переключение статуса закрыта/открыта вакансия"""
        vacancy = get_object_or_404(Vacancy, id=pk)
        vacancy.is_closed = not vacancy.is_closed
        vacancy.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyShelterVacancyViewSet(VacancyViewSet):
    """Вакансии приюта, небезопасные методы доступны только
        владельцам приютов. Все созданные вакансии автоматически попадают
        на вкладку вакансий приюта создателя."""
    permission_classes = (IsShelterOwner,)

    def get_queryset(self):
        shelter = self.request.user.shelter
        return Vacancy.objects.filter(shelter=shelter)

    def perform_create(self, serializer):
        shelter = self.request.user.shelter
        serializer.save(shelter=shelter)


class FAQViewSet(viewsets.ModelViewSet):
    """Ответы на часто задаваемые вопросы. Небезопасные методы доступны только
        администратору/модератору."""
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = (IsAdminModerOrReadOnly,)


class ScheduleViewSet(viewsets.ModelViewSet):
    """Графики работы для вакансий. Небезопасные методы доступны только
        администратору/модератору."""
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = (IsAdminModerOrReadOnly,)


class EducationViewSet(viewsets.ModelViewSet):
    """Образование для вакансий. Небезопасные методы доступны только
        администратору/модератору."""
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = (IsAdminModerOrReadOnly,)
