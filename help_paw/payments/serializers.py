from rest_framework import serializers

from payments.models import Donation


class DonateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('amount',)
        model = Donation
