import json

import pytest

pytestmark = pytest.mark.django_db


class TestNewsEndpoint:

    endpoint = '/api/v1/news/'

    def test_list(self, api_client, news_factory):

        news_factory.create_batch(3)
        response = api_client.get(self.endpoint)
        assert response.status_code == 200
        assert len(json.loads(response.content)) == 3


class TestFAQEndpoint:
    pass


class TestSheltersEndpoint:
    pass


class TestHelpArticlesEndpoint:
    pass


class TestPetsEndpoint:
    pass


class TestVacanciesEndpoint:
    pass


class TestAnimalTypesEndpoint:
    pass


class TestChatsEndpoint:
    pass


class TestUsersEndpoint:
    pass
