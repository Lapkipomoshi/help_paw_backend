from rest_framework import serializers

from chat.models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    pub_date = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S',
        read_only=True
    )
    is_readed = serializers.BooleanField(read_only=True)
    is_edited = serializers.BooleanField(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'author', 'text', 'pub_date', 'is_readed', 'is_edited')


class ChatSerializer(serializers.ModelSerializer):
    shelter = serializers.CharField(source='shelter.name', read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ('id', 'shelter', 'user', 'messages')
