from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsAdminModerOrReadOnly, IsShelterOwner
from info.models import News, Vacancy
from info.serializers import (NewsSerializer, NewsShortSerializer,
                              VacancySerializer)
from shelters.models import Shelter


class NewsViewSet(viewsets.ModelViewSet):
    """Новости приютов."""
    search_fields = ('header',)
    permission_classes = [IsAdminModerOrReadOnly, ]

    def get_queryset(self):
        if self.action == 'list':
            return News.objects.filter(on_main=True).select_related('shelter').only(
                'id', 'pub_date', 'profile_image', 'header', 'shelter__name'
            )
        else:
            return News.objects.filter(on_main=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return NewsShortSerializer
        else:
            return NewsSerializer

    def perform_create(self, serializer):
        serializer.save(on_main=True)


class ShelterNewsViewSet(viewsets.ReadOnlyModelViewSet):
    search_fields = ('header',)

    def get_queryset(self):
        shelter_id = self.kwargs.get('shelter_id')
        if self.action == 'list':
            return News.objects.filter(shelter=shelter_id).select_related('shelter').only(
                'id', 'pub_date', 'profile_image', 'header', 'shelter__name'
            )
        else:
            return News.objects.filter(shelter=shelter_id)

    def get_serializer_class(self):
        if self.action == 'list':
            return NewsShortSerializer
        else:
            return NewsSerializer


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

    @action(detail=True, methods=('patch', ), url_path='toggle-close')
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
