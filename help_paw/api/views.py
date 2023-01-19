from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated

from api.serializers import NewsSerializer, FAQSerializer
from info.models import News, FAQ


class NewsViewSet(viewsets.ModelViewSet):
    """Новости приютов"""
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter,)
    search_fields = ('header',)


class FAQViewSet(viewsets.ModelViewSet):
    """Ответы на часто задаваемые вопросы"""
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter,)
