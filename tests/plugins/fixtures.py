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


# # from rest_framework.permissions import IsAuthenticated
# from api.permissions import (IsOwnerAdminOrReadOnly, IsAdminModerOrReadOnly,
#                              IsShelterOwnerOrAdmin)
# from unittest import mock
#
#
# @pytest.fixture(scope="session", autouse=True)
# def mock_views_permissions():
#     # little util I use for testing for DRY when patching multiple objects
#     patch_perm = lambda perm: mock.patch.multiple(
#         perm,
#         has_permission=mock.Mock(return_value=True),
#         has_object_permission=mock.Mock(return_value=True),
#     )
#     with (
#         patch_perm(IsOwnerAdminOrReadOnly),
#         patch_perm(IsAdminModerOrReadOnly),
#         patch_perm(IsShelterOwnerOrAdmin),
#         # ...add other permissions you may have below
#     ):
#         yield
