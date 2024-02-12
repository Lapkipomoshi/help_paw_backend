from decimal import Decimal
from urllib.parse import urlencode

import requests
from django.conf import settings
from rest_framework.exceptions import APIException, ValidationError
from yookassa import Configuration, Payment, Webhook
from yookassa.domain.notification import PaymentWebhookNotification


def payment_create(amount: Decimal,
                   token: str,
                   shelter_id: int) -> tuple[str, str, str]:
    """Создает объект платежа Юкассы и возвращает его"""
    Configuration.configure_auth_token(token)
    is_test_payment = settings.DEBUG
    try:
        payment_object = Payment.create({
            "amount": {
                "value": f"{amount}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://lapkipomoshi.ru/shelters/{shelter_id}/about"
            },
            "capture": True,
            "refundable": False,
            "test": is_test_payment
        })
    except requests.exceptions.RequestException:
        raise APIException(detail='Yookassa service unavailable')
    external_id = payment_object.id
    created_at = payment_object.created_at
    confirmation_url = payment_object.confirmation.confirmation_url
    return external_id, created_at, confirmation_url


def add_webhooks_to_shelter(token: str) -> None:
    """Добавляет вебхук для платежей."""
    Configuration.configure_auth_token(token)
    try:
        Webhook.add({
            "event": "payment.succeeded",
            "url": "https://lapkipomoshi.ru/api/v1/payments/webhook-callback/",
        })
    except requests.exceptions.RequestException:
        raise APIException(detail='Yookassa service unavailable')


def get_payment_data(event_json: dict) -> tuple[str, bool, Decimal]:
    """Возвращает данные платежа для которого пришло
    оповещения об изменении статуса."""
    try:
        external_id = PaymentWebhookNotification(event_json).object.id
        payment_object = Payment.find_one(external_id)
        is_successful = payment_object.paid
        amount = payment_object.amount.value
    except Exception:
        raise APIException()
    return external_id, is_successful, amount


def get_oauth_token_for_shelter(code: str) -> tuple[str, int]:
    """Запрашивает OAuth токен для магазина партнера,
    возвращает токен и время его истечения в секундах."""
    url = 'https://yookassa.ru/oauth/v2/token'
    data = {'grant_type': 'authorization_code', 'code': code}
    auth = (settings.YOOKASSA_CLIENT_ID, settings.YOOKASSA_CLIENT_SECRET)
    try:
        response = requests.post(url=url, data=data, auth=auth)
    except requests.exceptions.RequestException:
        raise APIException(detail='Yookassa service unavailable')
    if response.status_code != 200:
        raise ValidationError(detail=response.json())
    data = response.json()
    access_token = data.get('access_token')
    expires_in_seconds = data.get('expires_in')
    return access_token, expires_in_seconds


def make_partner_link(state: str) -> str:
    """Создание ссылки для подключения к партнерской программе."""
    url = 'https://yookassa.ru/oauth/v2/authorize?'
    params = {
        'client_id': settings.YOOKASSA_CLIENT_ID,
        'response_type': 'code',
        'state': state
    }
    return url + urlencode(params)
