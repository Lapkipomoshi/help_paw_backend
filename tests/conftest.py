from pytest_factoryboy import register

from tests.plugins.factories import (AnimalTypeFactory, ChatFactory,
                                     FAQFactory, HelpArticleFactory,
                                     MessageFactory, NewsFactory, PetFactory,
                                     ShelterFactory, StaticInfoFactory,
                                     TaskFactory, UserFactory, VacancyFactory,
                                     UserPetFactory, UserShelterFactory)

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
register(ChatFactory)
register(MessageFactory)
register(UserPetFactory)
register(UserShelterFactory)

pytest_plugins = [
    'tests.plugins.fixtures',
    'tests.plugins.fixtures_for_endpoints',
]
