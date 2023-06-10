import datetime

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings as djoser_settings
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from api.serializers import (AnimalTypeSerializer, EmailSerializer,
                             FAQSerializer, HelpArticleSerializer,
                             HelpArticleShortSerializer, PetSerializer,
                             ShelterSerializer, ShelterShortSerializer)
from chat.models import Chat
from chat.serializers import ChatSerializer
from info.models import FAQ, HelpArticle
from shelters.models import AnimalType, Pet, Shelter

from .filters import PetFilter, SheltersFilter
from .permissions import IsAdminModerOrReadOnly, IsOwnerAdminOrReadOnly

User = get_user_model()


class FAQViewSet(viewsets.ModelViewSet):
    """Ответы на часто задаваемые вопросы."""
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    filter_backends = (SearchFilter,)
    permission_classes = (IsAdminModerOrReadOnly,)


class HelpArticleViewSet(viewsets.ModelViewSet):
    """Полезные статьи."""
    permission_classes = [IsAdminModerOrReadOnly, ]

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


class ShelterViewSet(viewsets.ModelViewSet):
    """Приюты."""
    filter_backends = [DjangoFilterBackend, SearchFilter, ]
    filterset_class = SheltersFilter
    search_fields = ('name', )
    permission_classes = [IsOwnerAdminOrReadOnly, ]

    def get_queryset(self, *args, **kwargs):
        if self.action in ('list', 'on_main',):
            return Shelter.approved.only(
                'id', 'name', 'address', 'working_from_hour',
                'working_to_hour', 'logo', 'profile_image', 'long', 'lat'
            )
        else:
            return Shelter.approved.all()

    def get_serializer_class(self):
        if self.action in ('list', 'on_main', ):
            return ShelterShortSerializer
        if self.action == 'start_chat':
            return ChatSerializer
        else:
            return ShelterSerializer

    @action(detail=False, methods=('get',), url_path='on-main')
    def on_main(self, request):
        """Список приютов для главной страницы."""
        queryset = self.get_queryset().order_by('?')
        return super().list(queryset)

    @action(detail=True, methods=('post',), url_path='start-chat')
    def start_chat(self, request, pk):
        shelter = get_object_or_404(Shelter, id=pk)
        chat = Chat.objects.get_or_create(shelter=shelter, user=request.user)
        serializer = self.get_serializer(chat[0])
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(owner=user)


class PetViewSet(viewsets.ModelViewSet):
    """Питомцы."""
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_class = PetFilter
    search_fields = ('name', )
    permission_classes = (IsOwnerAdminOrReadOnly, )

    @action(detail=True, methods=('patch', ))
    def adopt(self, request, pk):
        """Изменяет булево значение поля is_adopted модели Pet
        на противоположное."""
        pet = get_object_or_404(Pet, id=pk)
        pet.is_adopted = not pet.is_adopted
        pet.save()
        serializer = self.get_serializer(pet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnimalTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminModerOrReadOnly,)
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('shelters',)


class CustomUserViewSet(UserViewSet):
    def get_serializer_class(self):
        if self.action == 'reset_username':
            return EmailSerializer
        return super().get_serializer_class()

    def perform_update(self, serializer):
        serializer.save(raise_exception=True)

    @staticmethod
    def create_reset_email_token(email):
        exp = datetime.datetime.utcnow() + datetime.timedelta(days=2)
        data = {'email': email, 'exp': exp}
        token = jwt.encode(payload=data, key=settings.SECRET_KEY, algorithm='HS256')
        return token

    @action(["post"], detail=False, url_path="reset_{}".format(User.USERNAME_FIELD))
    def reset_username(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        email = serializer.validated_data.get('email')
        token = self.create_reset_email_token(email)

        if user:
            context = {'user': user, 'conf_token': token}
            to = [email]
            djoser_settings.EMAIL.username_reset(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)
