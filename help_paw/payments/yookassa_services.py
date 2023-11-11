from django.conf import settings
from rest_framework.exceptions import ValidationError
from yookassa import Configuration, Payment, Webhook
from yookassa.domain.notification import WebhookNotification
from yookassa.domain.response import PaymentResponse


def yookassa_payment_create(amount: float, token: str) -> PaymentResponse:
    Configuration.configure_auth_token(token)
    is_test_payment = settings.DEBUG
    yookassa_payment = Payment.create({
        "amount": {
            "value": f"{amount}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://lapkipomoshi.ru/"
        },
        "capture": True,
        "refundable": False,
        "test": is_test_payment
    })
    return yookassa_payment


def add_webhooks_to_shelter(token: str) -> None:
    Configuration.configure_auth_token(token)
    Webhook.add({
        "event": "payment.succeeded",
        "url": "https://lapkipomoshi.ru/api/v1/payments/webhook-callback/",
    })
    Webhook.add({
        "event": "payment.canceled",
        "url": "https://lapkipomoshi.ru/api/v1/payments/webhook-callback/",
    })


def parse_webhook_response(event_json: dict) -> WebhookNotification:
    try:
        notification_object = WebhookNotification(event_json)
    except Exception:
        raise ValidationError(code=400)
    return notification_object
