from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (FAQViewSet, HelpArticleViewSet, NewsViewSet, PetViewSet,
                       ShelterViewSet)

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register(r'news', NewsViewSet, basename="news")
v1_router.register(r'faq', FAQViewSet, basename="faq")
v1_router.register(r'shelters', ShelterViewSet, basename='shelters')
v1_router.register(
    r'help-articles', HelpArticleViewSet, basename='help_articles'
)
v1_router.register(
    r'pets', PetViewSet, basename='pets'
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
