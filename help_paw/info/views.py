from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.permissions import IsAdminModerOrReadOnly, IsShelterOwner
from info.models import News
from info.serializers import NewsSerializer, NewsShortSerializer


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
