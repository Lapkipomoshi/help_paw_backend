import pytest

pytestmark = pytest.mark.django_db(transaction=True)


class TestInfoModels:

    def test_news_str_method(self, news_factory):
        my_news = news_factory()

        assert my_news.__str__() == 'test_header'[:10]

    def test_help_str_method(self, help_article_factory):
        my_help_article = help_article_factory()

        assert my_help_article.__str__() == 'test_header'[:10]

    def test_faq_str_method(self, faq_factory):
        my_faq = faq_factory()

        assert my_faq.__str__() == 'test_question'

    def test_static_info_str_method(self, static_info_factory):
        my_static_info = static_info_factory()

        assert my_static_info.__str__() == 'test_about_us'

    def test_vacancy_str_method(self, vacancy_factory):
        my_vacancy = vacancy_factory()

        assert my_vacancy.__str__() == 'test_position'


class TestShelterModels:

    def test_animal_type_str_method(self, animal_type_factory):
        my_animal_type = animal_type_factory()

        assert my_animal_type.__str__() == 'test_animal_type'

    def test_pet_str_method(self, pet_factory):
        my_pet = pet_factory()

        assert my_pet.__str__() == 'test_name'

    def test_shelter_str_method(self, shelter_factory):
        my_shelter = shelter_factory()

        assert my_shelter.__str__() == 'test_name'

    def test_task_str_method(self, task_factory):
        my_task = task_factory()

        assert my_task.__str__() == 'test_name'

