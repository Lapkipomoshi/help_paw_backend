from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import NewsViewSet, FAQViewSet

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register(r'news', NewsViewSet, basename="news")
v1_router.register(r'faq', FAQViewSet, basename="faq")


urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
