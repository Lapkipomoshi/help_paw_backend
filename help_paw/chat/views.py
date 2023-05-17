from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.models import Chat
from chat.permissions import IsAuthor, IsShelterOwner
from chat.serializers import (ChatListSerializer, ChatSerializer,
                              MessageSerializer)


class ChatViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ChatListSerializer
        if self.action == 'send_message':
            return MessageSerializer
        return ChatSerializer

    @action(detail=True, methods=('post',), url_path='send-message')
    def send_message(self, request, pk):
        author = request.user
        chat = get_object_or_404(Chat, id=pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=author, chat=chat)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated and IsAuthor,)

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, id=chat_id)
        return chat.messages.all()

    def perform_update(self, serializer):
        serializer.save(is_edited=True)


class ShelterChatViewSet(ChatViewSet):
    permission_classes = (IsAuthenticated and IsShelterOwner,)

    def get_queryset(self):
        shelter = self.request.user.shelter
        return Chat.objects.filter(shelter=shelter)
