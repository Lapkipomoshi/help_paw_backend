from rest_framework import serializers

from info.models import News, FAQ


class NewsSerializer(serializers.ModelSerializer):
    """Новости приютов"""

    class Meta:
        fields = ('header', 'text', 'pub_date')
        model = News


class FAQSerializer(serializers.ModelSerializer):
    """Ответы на часто задаваемые вопросы"""

    class Meta:
        fields = ('question', 'answer')
        model = FAQ
