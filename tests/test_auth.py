import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.test import APIClient
import re

url_signup = '/api/auth/users/'
url_activation = '/api/auth/users/activation/'
url_jwt_create = '/api/auth/jwt/create/'

User = get_user_model()

pytestmark = pytest.mark.django_db(transaction=True)


def get_params_from_text(text, link_to_replace):
    """
    Вспомогательная функция, получает uid и token из текста письма
    при регистрации/смене пароля.
    """

    # из текста вытаскиваю урл
    url_pattern = re.compile(r'[\'"]?([^\'" >]+)')
    url = re.findall(url_pattern, text)
    # из урла вытаскиваю параметры
    params = re.findall(r'/([\w-]+)',
                        str(url).replace(link_to_replace, ''))
    return {
        'uid': params[0],
        'token': params[1]
    }


@pytest.mark.parametrize('url', [
    url_signup,
    url_jwt_create,
    url_activation
])
def test_url_is_reachable(client, url):
    """Проверка доступности энд-пойнтов."""
    response = client.post(url)
    assert response.status_code != status.HTTP_404_NOT_FOUND, (
        f'Страница `{url}` не найдена, проверьте доступность этого энд-пойнта!'
    )


def test_user_signup(client, new_user_data):
    """
    Проверка создания нового пользователя и отправки письма с
    активацией аккаунта на email.
    """
    warning_text = (
        f'Проверьте, что при POST-запросе на энд-пойнт {url_signup} ')

    response = client.post(url_signup)
    code = status.HTTP_400_BAD_REQUEST
    assert response.status_code == code, (
            warning_text + f'без параметров не создается пользователь и '
                           f'возвращается статус {code}'
    )

    outbox_before_count = len(mail.outbox)
    response = client.post(url_signup, new_user_data)
    outbox_after = mail.outbox

    assert response.status_code == status.HTTP_201_CREATED, (
            warning_text + 'создается новый пользователь.'
    )

    data = response.data

    assert data['email'] == new_user_data['email'], (
            warning_text + 'у созданного пользователя корректный e-mail.'
    )
    assert data['username'] == new_user_data['username'], (
            warning_text + 'у созданного пользователя корректный username.'
    )

    assert 'password' not in data, (
            warning_text + 'не возвращается пароль в явном виде.'
    )

    assert len(outbox_after) == outbox_before_count + 1, (
            warning_text + 'пользователю приходит email со ссылкой для '
                           'активации аккаунта.'
    )


def test_user_activation(client, new_user_data):
    """
    Проверка активации юзера по ссылке из письма, отправленного на email.
    """

    client.post(url_signup, new_user_data)
    user = User.objects.get(email=new_user_data.get('email'))
    outbox = mail.outbox

    assert not user.is_active and len(outbox) == 1, (
        'Проверьте, что в настройках Djoser включена активация нового '
        'пользователя по электронной почте.'
    )

    payload = get_params_from_text(outbox[0].body,
                                   'http://testserver/activate')
    response = client.post(url_activation, payload)
    user = User.objects.get(pk=user.pk)

    assert (response.status_code == status.HTTP_204_NO_CONTENT
            and user.is_active), (
        'Ошибка активации нового пользователя по email, проверьте настройки '
        'Djoser.'
    )


def test_jwt_token_create_refresh_verify(user, client, new_user_data):
    """
    Проверка получения токена для нового пользователя,
    верификация и обновление токена.
    """
    url_jwt_refresh = '/api/auth/jwt/refresh/'
    url_jwt_verify = '/api/auth/jwt/verify/'

    required_fields = ['refresh', 'access']
    warning_text = (
        f'Проверьте, что при POST-запросе на энд-пойнт {url_jwt_create} '
    )
    response = client.post(url_jwt_create, new_user_data)

    assert response.status_code == status.HTTP_200_OK, (
            warning_text + 'создается новый токен доступа.'
    )

    response_json = response.json()
    for field in required_fields:
        assert field in response_json, (
                warning_text + f'в ответ приходит созданный объект '
                               f'с полями {required_fields}'
        )

    response = client.post(url_jwt_refresh, response_json)
    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK, (
            warning_text + 'обновляется токен доступа.'
    )

    payload = {
        'token': response_json.get('access')
    }
    response = response.client.post(url_jwt_verify, payload)

    assert response.status_code == status.HTTP_200_OK, (
            warning_text + 'при обновлении возвращается новый валидный токен '
                           'доступа.'
    )


def test_users_reset_password(user, client, user_client, new_user_data):
    """Проверка возможности смены пароля"""

    url_reset = '/api/auth/users/reset_password/'
    url_confirm = '/api/auth/users/reset_password_confirm/'
    warning_text = 'Проверьте, что при POST-запросе на энд-пойнт '

    payload = {'email': user.email}

    response = user_client.post(url_reset, payload)
    outbox = mail.outbox

    assert (response.status_code == status.HTTP_204_NO_CONTENT and len(
        outbox) == 1), (
            warning_text + f'{url_reset} возвращается статус 204 и '
                           f'пользователю отправляется письмо со ссылкой для '
                           f'смены пароля.'
    )

    payload = get_params_from_text(outbox[0].body,
                                   'http://testserver/password-reset')
    new_passport = 'password_is_changed'
    payload['new_password'] = new_passport
    response = client.post(url_confirm, payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT, (
            warning_text + f'{url_confirm}  возвращается статус 204.'
    )

    new_client = APIClient()
    assert new_client.login(email=user.email, password=new_passport), (
            warning_text + f'{url_confirm} изменяется пароль пользователя.'
    )


def test_users_update(user, client, user_client, new_user_data):
    """
    Проверка возможности смены email, username.
    """

    warning_text = f'Проверьте, что при PUT-запросе на энд-пойнт '
    url_update = f'/api/auth/users/{user.pk}/'
    payload = {
        'email': "user_changed@helppaw.fake",
        "username": "User_Changed"
    }

    response = user_client.put(url_update, payload)
    outbox = mail.outbox
    assert response.status_code == status.HTTP_200_OK and len(outbox) == 1, (
            warning_text + f'{url_update}  возвращается статус 200 и '
                           f'пользователю отправляется письмо со ссылкой для '
                           f'обновления учетных данных.'
    )

    payload = get_params_from_text(outbox[0].body,
                                   'http://testserver/activate')
    response = client.post(url_activation, payload)
    user = User.objects.get(pk=user.pk)

    assert (response.status_code == status.HTTP_204_NO_CONTENT
            and user.username != new_user_data.get('username')
            and user.email != new_user_data.get('email')
            ), 'Ошибка при обновлении учетных данных пользователя.'


def test_users_same_email(client, new_user_data):
    response = client.post(url_signup, new_user_data)
    code = status.HTTP_201_CREATED
    assert response.status_code == code, (
        f'Проверьте, что при POST-запросе {url_signup} можно создать'
        f'пользователя и возвращается статус {code}'
    )

    response = client.post(url_signup, new_user_data)
    code = status.HTTP_400_BAD_REQUEST
    assert response.status_code == code, (
        f'Проверьте, что при POST-запросе {url_signup} нельзя создать '
        f'пользователя, email которого уже зарегистрирован и возвращается '
        f'статус {code}'
    )
