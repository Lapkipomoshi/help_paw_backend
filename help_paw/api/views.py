from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.serializers import NewsSerializer, FAQSerializer
from info.models import News, FAQ


class NewsViewSet(viewsets.ModelViewSet):
    """Новости приютов"""
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class FAQViewSet(viewsets.ModelViewSet):
    """Ответы на часто задаваемые вопросы"""
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
