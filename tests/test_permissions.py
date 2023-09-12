import factory
import pytest

pytestmark = pytest.mark.django_db(transaction=True)
scenario_is_admin_moder_or_read_only_list = [
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
]
scenario_is_admin_moder_auth_or_read_only_shelters_list = [
    ('user', True, 'post', 201),
    ('user', False, 'post', 401),
    ('user', True, 'get', 200),
    ('user', False, 'get', 200),
    ('shelter_owner', True, 'post', 400),
    ('shelter_owner', False, 'post', 401),
    ('shelter_owner', True, 'get', 200),
    ('shelter_owner', False, 'get', 200),
    ('moderator', True, 'post', 400),
    ('moderator', False, 'post', 401),
    ('moderator', True, 'get', 200),
    ('moderator', False, 'get', 200),
    ('admin', True, 'post', 400),
    ('admin', False, 'post', 401),
    ('admin', True, 'get', 200),
    ('admin', False, 'get', 200)
]
scenario_is_admin_moder_or_read_only_pets_list = [
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
]


class TestPermissions:

    @pytest.mark.parametrize('status, is_auth, method, status_code,',
                             scenario_is_admin_moder_or_read_only_list)
    def test_is_admin_moder_or_read_only(self, status,
                                         status_code,
                                         is_auth,
                                         method,
                                         api_client,
                                         user_factory,
                                         faq_factory,
                                         help_article_factory,
                                         animal_type_factory,
                                         news_factory,
                                         schedule_factory,
                                         education_factory,
                                         ):

        data = {'/api/v1/faq/': faq_factory,
                '/api/v1/help-articles/': help_article_factory,
                '/api/v1/animal-types/': animal_type_factory,
                '/api/v1/news/': news_factory,
                '/api/v1/schedules/': schedule_factory,
                '/api/v1/educations/': education_factory,
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

    @pytest.mark.parametrize('status, is_auth, method, status_code,',
                             scenario_is_admin_moder_or_read_only_list)
    def test_is_admin_moder_or_read_only_vacancies(self,
                                                   status,
                                                   status_code,
                                                   is_auth,
                                                   method,
                                                   api_client,
                                                   user_factory,
                                                   vacancy_factory,
                                                   schedule_factory,
                                                   education_factory,
                                                   ):

        url = '/api/v1/vacancies/'
        user = user_factory.create(status=status)
        if is_auth:
            api_client.force_authenticate(user=user)

        if method == 'post':

            schedule = schedule_factory.create()
            education = education_factory.create()
            payload = factory.build(
                dict,
                FACTORY_CLASS=vacancy_factory,
                education=education.slug,
                schedule=[schedule.slug, ]
            )
            response = api_client.post(url, payload)
        else:
            response = api_client.get(url)

        assert response.status_code == status_code, (
            f'status={status}, '
            f'url={url}, '
            f'status_code={response.status_code}'
        )

    @pytest.mark.parametrize('status, is_auth, method, status_code,',
                             scenario_is_admin_moder_auth_or_read_only_shelters_list)
    def test_is_admin_moder_auth_or_read_only_shelters(self,
                                                       status,
                                                       status_code,
                                                       is_auth,
                                                       method,
                                                       api_client,
                                                       user_factory,
                                                       shelter_factory,
                                                       animal_type_factory,
                                                       ):

        url = '/api/v1/shelters/'
        user = user_factory.create(status=status)
        if is_auth:
            api_client.force_authenticate(user=user)

        if method == 'post':
            my_type = animal_type_factory.create()

            payload = factory.build(
                dict,
                FACTORY_CLASS=shelter_factory,
                animal_types=[my_type.slug, ]

            )
            response = api_client.post(url, payload)
        else:
            response = api_client.get(url)

        assert response.status_code == status_code, (
            f'status={status}, '
            f'url={url}, '
            f'status_code={response.status_code}'
        )

    @pytest.mark.parametrize('status, is_auth, method, status_code,',
                             scenario_is_admin_moder_or_read_only_pets_list
                             )
    def test_is_admin_moder_or_read_only_pets(self,
                                              status,
                                              status_code,
                                              is_auth,
                                              method,
                                              api_client,
                                              user_factory,
                                              shelter_factory,
                                              animal_type_factory,
                                              pet_factory
                                              ):

        user = user_factory.create(status=status)
        my_shelter = shelter_factory()
        pet_factory.create(shelter=my_shelter)
        url = f'/api/v1/shelters/{my_shelter.pk}/pets/'

        if is_auth:
            api_client.force_authenticate(user=user)

        if method == 'post':
            my_type = animal_type_factory.create()
            payload = factory.build(
                dict,
                FACTORY_CLASS=pet_factory,
                shelter=my_shelter.pk,
                animal_type=my_type.slug
            )
            response = api_client.post(url, payload)
        else:
            response = api_client.get(url)

        assert response.status_code == status_code, (
            f'status={status}, '
            f'url={url}, '
            f'status_code={response.status_code}'
        )
