from datetime import timedelta
from decimal import Decimal

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from payments.models import Donation, YookassaOAuthToken
from payments.yookassa_services import (add_webhooks_to_shelter,
                                        get_oauth_token_for_shelter,
                                        make_partner_link,
                                        parse_webhook_callback,
                                        yookassa_payment_create)
from shelters.models import Shelter

User = get_user_model()


def get_payment_confirm_url(amount: Decimal,
                            user: User | None,
                            shelter_id: int
                            ) -> dict[str, str]:
    """Создает запись пожертвования в БД,
    возвращает ссылку для подтверждения платежа."""
    oauth_token = get_object_or_404(YookassaOAuthToken, shelter=shelter_id)
    payment_confirm_url, external_id = yookassa_payment_create(amount,
                                                               oauth_token.token)
    Donation.objects.get_or_create(
        shelter=oauth_token.shelter,
        user=user,
        amount=amount,
        external_id=external_id)
    return {'payment_confirm_url': payment_confirm_url}


def finish_payment(event_json: dict) -> None:
    """Изменяет поле is_successful пожертвования в БД на True или удаляет его."""
    external_id, is_successful = parse_webhook_callback(event_json)
    payment = get_object_or_404(Donation, external_id=external_id)
    if is_successful:
        payment.is_successful = True
        payment.save()
    else:
        payment.delete()


def get_partner_link(user: User) -> dict[str, str]:
    """Возврвщает ссылку для подключения к партнерской программе."""
    shelter_tin = get_object_or_404(Shelter, owner=user).tin
    state = jwt.encode(
        payload={'tin': shelter_tin},
        key=settings.SECRET_KEY,
        algorithm='HS256')
    partner_link = make_partner_link(state)
    return {'partner_link': partner_link}


def add_oauth_token_with_webhooks_to_shelter(code: str | None,
                                             error: str | None,
                                             state: str
                                             ) -> None:
    """Записывает OAuth токен приюта в БД,
    и привязывает к нему вебхуки о статусах пожертвований."""
    if error is not None:
        raise ValidationError(detail=error)
    try:
        decode = jwt.decode(state, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.DecodeError:
        raise ValidationError(detail='Неверный параметр "state"')
    access_token, expires_in_seconds = get_oauth_token_for_shelter(code)
    add_webhooks_to_shelter(access_token)
    shelter = get_object_or_404(Shelter, tin=decode.get('tin'))
    expires_at = timezone.now() + timedelta(seconds=expires_in_seconds)
    YookassaOAuthToken.objects.create(shelter=shelter,
                                      token=access_token,
                                      expires_at=expires_at)
