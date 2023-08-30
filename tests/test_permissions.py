import factory
import pytest

pytestmark = pytest.mark.django_db(transaction=True)


class TestPermissions:

    @pytest.mark.parametrize('status, is_auth, method, status_code,', [
        ('user', True, 'post', 403),
        ('user', False, 'post', 401),
        ('user', True, 'get', 200),
        ('user', False, 'get', 200),
        ('shelter_owner', True, 'post', 403),
        ('shelter_owner', False, 'post', 401),
        ('shelter_owner', True, 'get', 200),
        ('shelter_owner', False, 'get', 200),
        ('moderator', True, 'post', 201),
        ('moderator', False, 'post', 401),
        ('moderator', True, 'get', 200),
        ('moderator', False, 'get', 200),
        ('admin', True, 'post', 201),
        ('admin', False, 'post', 401),
        ('admin', True, 'get', 200),
        ('admin', False, 'get', 200)
    ])
    def test_is_admin_moder_or_read_only_has_permission(self, status,
                                                        status_code,
                                                        is_auth,
                                                        method,
                                                        api_client,
                                                        faq_factory,
                                                        help_article_factory,
                                                        animal_type_factory,
                                                        news_factory,
                                                        user_factory):
        data = {'/api/v1/faq/': faq_factory,
                '/api/v1/help-articles/': help_article_factory,
                '/api/v1/animal-types/': animal_type_factory,
                '/api/v1/news/': news_factory
                }

        user = user_factory.create(status=status)
        if is_auth:
            api_client.force_authenticate(user=user)

        for url, factory_class in data.items():
            if method == 'post':
                payload = factory.build(
                    dict,
                    FACTORY_CLASS=factory_class,
                )
                response = api_client.post(url, payload)
            else:
                response = api_client.get(url)

            assert response.status_code == status_code, (
                f'status={status}, '
                f'url={url}, '
                f'status_code={response.status_code}'
            )
