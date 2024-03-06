import logging
from datetime import timedelta
from decimal import Decimal

import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from payments.models import Donation, YookassaOAuthToken
from payments.yookassa_services import (add_webhooks_to_shelter,
                                        get_oauth_token_for_shelter,
                                        get_payment_object, make_partner_link,
                                        payment_create)
from shelters.models import Shelter
from users.models import User

logger = logging.getLogger('payments')


def get_payment_confirm_url(amount: Decimal,
                            user: User,
                            shelter_id: int) -> str:
    """Создает запись пожертвования в БД,
    возвращает ссылку для подтверждения платежа."""
    logger.debug(f'{user if user.is_authenticated else None}')
    oauth_token = get_object_or_404(YookassaOAuthToken, shelter=shelter_id)
    payment_obj = payment_create(amount, oauth_token.token, shelter_id)
    Donation.objects.create(
        shelter=oauth_token.shelter,
        user=user if user.is_authenticated else None,
        amount=amount,
        external_id=payment_obj.id,
        created_at=payment_obj.created_at
    )
    return payment_obj.confirmation.confirmation_url


def finish_payment(event_json: dict) -> None:
    """Изменяет поле is_successful и сумму пожертвования в БД
    или удаляет его, на основе статуса платежа."""
    payment_object = get_payment_object(event_json)
    donation = get_object_or_404(Donation, external_id=payment_object.id)
    if payment_object.paid:
        donation.is_successful = True
        donation.amount = payment_object.amount.value
        donation.save()
    donation.delete()


def get_partner_link(user: User) -> str:
    """Возврвщает ссылку для подключения к партнерской программе."""
    shelter_tin = get_object_or_404(Shelter, owner=user).tin
    state = jwt.encode(
        payload={'tin': shelter_tin},
        key=settings.SECRET_KEY,
        algorithm='HS256')
    return make_partner_link(state)


def add_oauth_token_with_webhooks_to_shelter(code: str | None,
                                             error: str | None,
                                             state: str) -> None:
    """Записывает OAuth токен приюта в БД,
    и привязывает к нему вебхуки о статусах пожертвований."""
    if error:
        raise ValidationError(detail=error)
    try:
        tin = jwt.decode(state, settings.SECRET_KEY, algorithms=['HS256']).get('tin')
    except jwt.DecodeError:
        raise ValidationError(detail='Неверный параметр "state"')
    token_data = get_oauth_token_for_shelter(code)
    oauth_token = token_data.get('access_token')
    expires_in_seconds = token_data.get('expires_in')
    add_webhooks_to_shelter(oauth_token)
    shelter = get_object_or_404(Shelter, tin=tin)
    expires_at = timezone.now() + timedelta(seconds=expires_in_seconds)
    YookassaOAuthToken.objects.update_or_create(
        shelter=shelter,
        defaults={'token': oauth_token, 'expires_at': expires_at}
    )
