import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
import re

url_signup = '/api/auth/users/'
url_activation = '/api/auth/users/activation/'
url_jwt_create = '/api/auth/jwt/create/'

User = get_user_model()


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


@pytest.mark.django_db(transaction=True)
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


@pytest.mark.django_db(transaction=True)
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

    # Из тела письма получаю uid и token активации
    html_text = outbox[0].html

    url_pattern = re.compile(r'href=[\'"]?([^\'" >]+)')
    url = re.findall(url_pattern, html_text)
    params = re.findall(r'/([\w-]+)',
                        str(url).replace('http://testserver/activate', ''))
    data = {
        'uid': params[0],
        'token': params[1]
    }

    response = client.post(url_activation, data)
    user = User.objects.get(pk=user.pk)

    assert (response.status_code == status.HTTP_204_NO_CONTENT
            and user.is_active), (
        'Ошибка активации нового пользователя по email, проверьте настройки '
        'Djoser.'
    )


@pytest.mark.django_db(transaction=True)
def test_jwt_token_create_refresh_verify(client, user, new_user_data):
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

    data = {
        'token': response_json.get('access')
    }
    response = response.client.post(url_jwt_verify, data)

    assert response.status_code == status.HTTP_200_OK, (
            warning_text + 'при обновлении возвращается новый валидный токен '
                           'доступа.'
    )


@pytest.mark.django_db(transaction=True)
def test_auth_users_list():
    """
    Проверка получения списка пользователей для авторизованного и
    неавторизованного пользователей.
    """
    pass
