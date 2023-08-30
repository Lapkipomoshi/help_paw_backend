from pytest_factoryboy import register

from tests.plugins.factories import (AnimalTypeFactory, ChatFactory,
                                     EducationFactory, FAQFactory,
                                     HelpArticleFactory, MessageFactory,
                                     NewsFactory, PetFactory, ScheduleFactory,
                                     ShelterFactory, StaticInfoFactory,
                                     TaskFactory, UserFactory, UserPetFactory,
                                     UserShelterFactory, VacancyFactory)

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
register(ScheduleFactory)
register(EducationFactory)

pytest_plugins = [
    'tests.plugins.fixtures',
]
