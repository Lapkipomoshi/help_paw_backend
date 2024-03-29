from django.urls import include, path
from rest_framework.routers import DefaultRouter

from chat.views import ChatViewSet, MessageViewSet, MyShelterChatViewSet
from info.views import (EducationViewSet, FAQViewSet, HelpArticleViewSet,
                        MyShelterNewsViewSet, MyShelterVacancyViewSet,
                        NewsViewSet, ScheduleViewSet, VacancyViewSet)
from shelters.views import (AnimalTypeViewSet, MyShelterPetViewSet,
                            MyShelterViewSet, PetViewSet, ShelterViewSet)
from users.views import CustomUserViewSet

app_name = 'api'

v1_router = DefaultRouter()
user_router = DefaultRouter()
v1_router.register(r'news', NewsViewSet, basename='news')
v1_router.register(r'shelters/(?P<shelter_id>\d+)/news', NewsViewSet,
                   basename='shelter_news')
v1_router.register(r'my-shelter/news', MyShelterNewsViewSet,
                   basename='my_shelter_news')
v1_router.register(r'vacancies', VacancyViewSet, basename='vacancies')
v1_router.register(r'shelters/(?P<shelter_id>\d+)/vacancies', VacancyViewSet,
                   basename='shelter_vacancies')
v1_router.register(r'my-shelter/vacancies', MyShelterVacancyViewSet,
                   basename='my_shelter_vacancies')
v1_router.register(r'faq', FAQViewSet, basename='faq')
v1_router.register(r'shelters', ShelterViewSet, basename='shelters')
v1_router.register(r'help-articles', HelpArticleViewSet,
                   basename='help_articles')
v1_router.register(r'shelters/(?P<shelter_id>\d+)/pets', PetViewSet,
                   basename='pets')
v1_router.register(r'my-shelter/pets', MyShelterPetViewSet,
                   basename='my_shelter_pets')
v1_router.register(r'animal-types', AnimalTypeViewSet, basename='animal_types')
v1_router.register(r'chats', ChatViewSet, basename='chats')
v1_router.register(r'my-shelter/chats', MyShelterChatViewSet,
                   basename='my_shelter_chats')
v1_router.register(r'chats/(?P<chat_id>\d+)/messages', MessageViewSet,
                   basename='messages')
v1_router.register(r'my-shelter', MyShelterViewSet, basename='my_shelter')
v1_router.register(r'schedules', ScheduleViewSet, basename='schedules')
v1_router.register(r'educations', EducationViewSet, basename='educations')
user_router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/payments/', include('payments.urls')),
    path('auth/', include(user_router.urls)),
    path('auth/', include('djoser.urls.jwt')),
]
