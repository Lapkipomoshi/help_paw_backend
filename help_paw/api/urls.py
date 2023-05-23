from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (AnimalTypeViewSet, CustomUserViewSet, FAQViewSet,
                       HelpArticleViewSet, PetViewSet, ShelterViewSet,
                       VacancyViewSet)
from chat.views import ChatViewSet, MessageViewSet, MyShelterChatViewSet
from info.views import MyShelterNewsViewSet, NewsViewSet, ShelterNewsViewSet

app_name = 'api'

v1_router = DefaultRouter()
user_router = DefaultRouter()
v1_router.register(r'news', NewsViewSet, basename='news')
v1_router.register(r'shelters/(?P<shelter_id>\d+)/news', ShelterNewsViewSet, basename='shelter_news')
v1_router.register(r'my-shelter/news', MyShelterNewsViewSet, basename='my_shelter_news')
v1_router.register(r'faq', FAQViewSet, basename="faq")
v1_router.register(r'shelters', ShelterViewSet, basename='shelters')
v1_router.register(r'help-articles', HelpArticleViewSet, basename='help_articles')
v1_router.register(r'pets', PetViewSet, basename='pets')
v1_router.register(r'vacancies', VacancyViewSet, basename='vacancies')
v1_router.register(r'animal-types', AnimalTypeViewSet, basename='animal_types')
v1_router.register(r'chats', ChatViewSet, basename='chats')
v1_router.register(r'my-shelter/chats', MyShelterChatViewSet, basename='my_shelter_chats')
v1_router.register(r'chats/(?P<chat_id>\d+)/messages', MessageViewSet, basename='messages')
user_router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('auth/', include(user_router.urls)),
    path('auth/', include('djoser.urls.jwt')),
]
