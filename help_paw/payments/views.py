import json
import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsShelterOwner
from payments.serializers import DonateSerializer
from payments.services import (add_oauth_token_with_webhooks_to_shelter,
                               finish_payment, get_partner_link,
                               get_payment_confirm_url)

logger = logging.getLogger('payments')


@permission_classes((IsAuthenticated, AllowAny))
@api_view(['POST'])
def donate(request, shelter_id: int):
    logger.debug(f'{request.user} is {request.user.is_authenticated}')
    serializer = DonateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    confirmation_url = get_payment_confirm_url(
        amount=serializer.validated_data.get('amount'),
        user=request.user,
        shelter_id=shelter_id)
    return Response(data={'payment_confirm_url': confirmation_url},
                    status=status.HTTP_201_CREATED)


@api_view(['POST'])
def webhook_callback(request):
    event_json = json.loads(request.body)
    finish_payment(event_json)
    return Response(status=status.HTTP_200_OK)


@permission_classes((IsShelterOwner,))
@api_view(['GET'])
def partner_link(request):
    url = get_partner_link(request.user)
    return Response(data={'partner_link': url}, status=status.HTTP_200_OK)


@api_view(['GET'])
def partner_link_callback(request):
    code = request.query_params.get('code')
    error = request.query_params.get('error')
    state = request.query_params.get('state')
    add_oauth_token_with_webhooks_to_shelter(code, error, state)
    return Response(data='Your shelter successfully added to partner program',
                    status=status.HTTP_201_CREATED)
