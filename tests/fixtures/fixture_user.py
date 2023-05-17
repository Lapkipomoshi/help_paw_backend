import pytest


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
def user(django_user_model):
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
    from rest_framework_simplejwt.tokens import AccessToken
    token = AccessToken.for_user(user)

    return {
        'access': str(token),
    }