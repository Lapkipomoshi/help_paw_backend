from pytest_factoryboy import register
from .factories import (NewsFactory, HelpArticleFactory, FAQFactory,
                        StaticInfoFactory, VacancyFactory, ShelterFactory,
                        AnimalTypeFactory, PetFactory, UserFactory,
                        TaskFactory)

register(NewsFactory)
register(HelpArticleFactory)
register(FAQFactory)
register(StaticInfoFactory)
register(VacancyFactory)
register(ShelterFactory)
register(AnimalTypeFactory)
register(PetFactory)
register(UserFactory)
register(TaskFactory)

pytest_plugins = [
    'tests.fixtures.fixture_user',
]
