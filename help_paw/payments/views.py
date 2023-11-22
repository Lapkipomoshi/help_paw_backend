import json

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from api.permissions import IsShelterOwner
from payments.serializers import DonateSerializer
from payments.services import (add_oauth_token_with_webhooks_to_shelter,
                               finish_payment, get_partner_link,
                               get_payment_confirm_url)


@api_view(['POST'])
def donate(request, shelter_id: int):
    serializer = DonateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = request.user
    payment_confirm_url = get_payment_confirm_url(
        amount=serializer.validated_data.get('amount'),
        user=user if user.is_authenticated else None,
        shelter_id=shelter_id)
    return Response(data=payment_confirm_url, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def webhook_callback(request):
    event_json = json.loads(request.body)
    finish_payment(event_json)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsShelterOwner,))
def partner_link(request):
    url = get_partner_link(request.user)
    return Response(data=url, status=status.HTTP_200_OK)


@api_view(['GET'])
def partner_link_callback(request):
    code = request.query_params.get('code')
    error = request.query_params.get('error')
    state = request.query_params.get('state')
    add_oauth_token_with_webhooks_to_shelter(code, error, state)
    return Response(status=status.HTTP_201_CREATED)
