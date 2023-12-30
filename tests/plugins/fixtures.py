import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken


@pytest.fixture
def new_user_data():
    return {
        'email': 'user@helppaw.fake',
        'username': 'User',
        'password': 'User_12345',
        'is_active': False,
    }


@pytest.fixture
def superuser(django_user_model):
    return django_user_model.objects.create_superuser(
        username='Superuser',
        email='superuser@helppaw.fake',
        password='superuser_12345',
    )


@pytest.fixture
def defaultuser(django_user_model):
    return django_user_model.objects.create_user(
        username='User',
        email='user@helppaw.fake',
        password='User_12345',
        status='user',
    )


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_user(
        username='AdminUser',
        email='adminuser@helppaw.fake',
        password='AdminUser_12345',
        status='admin',
    )


@pytest.fixture
def moderator(django_user_model):
    return django_user_model.objects.create_user(
        username='ModeratorUser',
        email='moderatoruser@helppaw.fake',
        password='ModeratorUser_12345',
        status='moderator',
    )


@pytest.fixture
def shelter_owner(django_user_model):
    return django_user_model.objects.create_user(
        username='ShelterOwnerUser',
        email='shelterowneruser@helppaw.fake',
        password='ShelterOwnerUser_12345',
        status='shelter_owner',
    )


@pytest.fixture
def token_user(user):
    token = AccessToken.for_user(user)
    return {
        'access': str(token),
    }


@pytest.fixture
def token_admin(admin):
    token = AccessToken.for_user(admin)
    return {
        'access': str(token),
    }


@pytest.fixture
def user_client(token_user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_user["access"]}')
    return client


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_client(token_admin):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_admin["access"]}')
    return client
