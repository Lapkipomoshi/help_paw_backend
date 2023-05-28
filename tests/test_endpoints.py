import pytest


class TestNewsEndpoint:

    endpoint = '/api/v1/news/'

    @pytest.mark.django_db
    def test_get_news_not_authorised(self, client, news_factory):
        """ GET запрос доступен для неавторизованных пользователей """
        news_factory.create_batch(3)
        response = client.get(self.endpoint)
        assert response.status_code == 200
        assert len(response.json()) == 3

    @pytest.mark.django_db
    def test_post_news_not_authorised(self, client):
        """ POST запрос не доступен для неавторизованных пользователей """
        response = client.post(self.endpoint)
        assert response.status_code == 401


class TestFAQEndpoint:
    endpoint = '/api/v1/faq/'

    @pytest.mark.django_db
    def test_get_faq_not_authorised(self, client, faq_factory):
        """ GET запрос доступен для неавторизованных пользователей """
        faq_factory()
        response = client.get(self.endpoint)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_post_faq_not_authorised(self, client):
        """ POST запрос не доступен для неавторизованных пользователей """
        response = client.post(self.endpoint)
        assert response.status_code == 401


class TestSheltersEndpoint:
    endpoint = '/api/v1/shelters/'

    @pytest.mark.django_db
    def test_get_shelters_not_authorised(self, client, shelter_factory):
        """ GET запрос доступен для неавторизованных пользователей """
        shelter_factory()
        response = client.get(self.endpoint)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_post_shelters_not_authorised(self, client):
        """ POST запрос не доступен для неавторизованных пользователей """
        response = client.post(self.endpoint)
        assert response.status_code == 401


class TestHelpArticlesEndpoint:
    endpoint = '/api/v1/help-articles/'

    @pytest.mark.django_db
    def test_get_help_articles_not_authorised(self, client,
                                              help_article_factory):
        """ GET запрос доступен для неавторизованных пользователей """
        help_article_factory()
        response = client.get(self.endpoint)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_post_help_articles_not_authorised(self, client):
        """ POST запрос не доступен для авторизованных пользователей """
        response = client.post(self.endpoint)
        assert response.status_code == 401


class TestPetsEndpoint:
    endpoint = '/api/v1/pets/'

    @pytest.mark.django_db
    def test_get_pets_not_authorised(self, client, pet_factory):
        """ GET запрос доступен для неавторизованных пользователей """
        pet_factory()
        response = client.get(self.endpoint)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_post_pets_not_authorised(self, client):
        """ POST запрос не доступен для неавторизованных пользователей """
        response = client.post(self.endpoint)
        assert response.status_code == 401


class TestVacanciesEndpoint:
    endpoint = '/api/v1/vacancies/'

    @pytest.mark.django_db
    def test_get_vacancies_not_authorised(self, client, vacancy_factory):
        """ GET запрос доступен для неавторизованных пользователей """
        vacancy_factory()
        response = client.get(self.endpoint)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_post_vacancies_not_authorised(self, client):
        """ POST запрос не доступен для неавторизованных пользователей """
        response = client.post(self.endpoint)
        assert response.status_code == 401


class TestAnimalTypesEndpoint:
    endpoint = '/api/v1/animal-types/'

    @pytest.mark.django_db
    def test_get_animal_types(self, client, animal_type_factory):
        animal_type_factory()
        response = client.get(self.endpoint)
        assert response.status_code == 200
        assert set(response.data[0].keys()) == {'id', 'name', 'slug'}

    # пока пропускаем, до выяснения про POST для анонимов
    @pytest.mark.skip
    # @pytest.mark.django_db
    def test_post_animal_types(self, client, animal_type_factory):
        """Проверяем, что работает только GET-запрос"""
        data = {"name": "попугай", "slug": "parrot"}
        assert client.post(self.endpoint, data).status_code == 405
        assert client.put(self.endpoint, data).status_code == 405
        assert client.patch(self.endpoint, data).status_code == 405
        assert client.delete(self.endpoint).status_code == 405


class TestChatsEndpoint:
    endpoint = '/api/v1/chats/'

    @pytest.mark.django_db
    def test_get_chats_not_authorised(self, client, chat_factory):
        """ /chats/ не доступен для неавторизованных пользователей."""
        chat_factory()
        response = client.get(self.endpoint)
        assert response.status_code == 401

    @pytest.mark.django_db
    def test_get_chats_authorised(self, user_client):
        """ /chats/ доступен для авторизованных пользователей."""
        response = user_client.get(self.endpoint)
        assert response.status_code == 200


class TestUsersEndpoint:
    endpoint = '/api/auth/users/'

    @pytest.mark.django_db
    def test_get_users_not_authorised(self, client, user_factory):
        """ /auth/users/ доступен для неавторизованных пользователей """
        user_factory()
        response = client.get(self.endpoint)
        assert response.status_code == 200
        assert response.data == []

    @pytest.mark.django_db
    def test_get_users_authorised(self, user_client, user_factory):
        """ /auth/users/ доступен для авторизованных пользователей """
        user_factory()
        response = user_client.get(self.endpoint)
        assert response.status_code == 200
        assert response.data != []
