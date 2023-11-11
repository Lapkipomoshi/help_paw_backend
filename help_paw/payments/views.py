import json

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from payments.serializers import DonateSerializer
from payments.services import finish_payment, get_payment_confirm_url


@api_view(['POST'])
def donate(request, shelter_id):
    serializer = DonateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    payment_confirm_url = get_payment_confirm_url(
        amount=serializer.validated_data.get('amount'),
        user_id=request.user.id,
        shelter_id=shelter_id)
    return Response(data=payment_confirm_url, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def webhook_callback(request):
    event_json = json.loads(request.body)
    finish_payment(event_json)
    return Response(status=status.HTTP_200_OK)
