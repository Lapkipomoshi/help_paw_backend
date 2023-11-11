from typing import Optional

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from payments.models import Payment, YookassaOAuthToken
from payments.yookassa_services import (parse_webhook_response,
                                        yookassa_payment_create)

User = get_user_model()


def get_payment_confirm_url(amount: float, user_id: Optional[int], shelter_id: int
                            ) -> str:
    oauth_token = get_object_or_404(YookassaOAuthToken, shelter=shelter_id)
    if user_id:
        user = User.objects.get(id=user_id)
    else:
        user = None
    payment = yookassa_payment_create(amount, oauth_token.token)
    Payment.objects.get_or_create(
        shelter=oauth_token.shelter, user=user, amount=amount, external_id=payment.id)
    return payment.confirmation.confirmation_url


def finish_payment(event_json: dict) -> None:
    notification_object = parse_webhook_response(event_json)
    payment = get_object_or_404(Payment, external_id=notification_object.object.id)
    status = notification_object.object.status
    if status == 'succeeded':
        payment.is_successful = True
        payment.save()
    elif status == 'canceled':
        payment.delete()
    else:
        raise ValidationError(code=400)
