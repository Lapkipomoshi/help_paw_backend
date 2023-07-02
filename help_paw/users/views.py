import datetime

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from djoser.conf import settings as djoser_settings
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.serializers import EmailSerializer

User = get_user_model()


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
        token = jwt.encode(payload=data, key=settings.SECRET_KEY,
                           algorithm='HS256')
        return token

    @action(["post"], detail=False,
            url_path="reset_{}".format(User.USERNAME_FIELD))
    def reset_username(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        email = serializer.validated_data.get('email')
        token = self.create_reset_email_token(email)

        if user:
            context = {'user': user, 'conf_token': token}
            to = [email]
            djoser_settings.EMAIL.username_reset(self.request, context).send(
                to)

        return Response(status=status.HTTP_204_NO_CONTENT)
