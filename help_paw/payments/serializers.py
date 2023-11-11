from rest_framework import serializers


class DonateSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True, min_value=1.0)
