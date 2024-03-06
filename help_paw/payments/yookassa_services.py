import logging
from decimal import Decimal
from urllib.parse import urlencode

import requests
from django.conf import settings
from rest_framework.exceptions import APIException, ParseError
from yookassa import Configuration, Payment, Webhook
from yookassa.domain.notification import PaymentWebhookNotification
from yookassa.domain.response import PaymentResponse

logger = logging.getLogger('payments')


def payment_create(amount: Decimal,
                   token: str,
                   shelter_id: int) -> PaymentResponse:
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
    except requests.exceptions.ConnectionError as e:
        logger.warning(e)
        raise APIException('Yookassa service unavailable')
    except requests.exceptions.HTTPError as e:
        logger.error(e.response.text)
        raise ParseError()
    return payment_object


def add_webhooks_to_shelter(token: str) -> None:
    """Добавляет вебхук для платежей."""
    Configuration.configure_auth_token(token)
    try:
        Webhook.add({
            "event": "payment.succeeded",
            "url": "https://lapkipomoshi.ru/api/v1/payments/webhook-callback/",
        })
        Webhook.add({
            "event": "payment.canceled",
            "url": "https://lapkipomoshi.ru/api/v1/payments/webhook-callback/",
        })
    except requests.exceptions.ConnectionError as e:
        logger.warning(e)
        raise APIException('Yookassa service unavailable')
    except requests.exceptions.HTTPError as e:
        logger.error(e.response.text)
        raise ParseError()


def get_payment_object(event_json: dict) -> PaymentResponse:
    """Возвращает данные платежа для которого пришло
    оповещения об изменении статуса."""
    external_id = PaymentWebhookNotification(event_json).object.id
    try:
        payment_object = Payment.find_one(external_id)
    except requests.exceptions.ConnectionError as e:
        logger.warning(e)
        raise APIException('Yookassa service unavailable')
    except requests.exceptions.HTTPError as e:
        logger.error(e.response.text)
        raise ParseError()
    return payment_object


def get_oauth_token_for_shelter(code: str) -> dict[str, str | int]:
    """Запрашивает OAuth токен для магазина партнера,
    возвращает токен и время его истечения в секундах."""
    url = 'https://yookassa.ru/oauth/v2/token'
    data = {'grant_type': 'authorization_code', 'code': code}
    auth = (settings.YOOKASSA_CLIENT_ID, settings.YOOKASSA_CLIENT_SECRET)
    try:
        response = requests.post(url=url, data=data, auth=auth)
    except requests.exceptions.ConnectionError as e:
        logger.warning(e)
        raise APIException('Yookassa service unavailable')
    except requests.exceptions.HTTPError as e:
        logger.error(e.response.text)
        raise ParseError()
    token_data = response.json()
    if response.status_code != 200:
        logger.error(token_data)
        raise ParseError()
    return token_data


def make_partner_link(state: str) -> str:
    """Создание ссылки для подключения к партнерской программе."""
    url = 'https://yookassa.ru/oauth/v2/authorize?'
    params = {
        'client_id': settings.YOOKASSA_CLIENT_ID,
        'response_type': 'code',
        'state': state
    }
    return url + urlencode(params)
