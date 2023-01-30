from django.contrib import admin

from info.models import (FAQ, HelpArticle, News, OwnVacancy, ShelterVacancy,
                         StaticInfo)

admin.site.register(FAQ)
admin.site.register(News)
admin.site.register(OwnVacancy)
admin.site.register(StaticInfo)
admin.site.register(ShelterVacancy)
admin.site.register(HelpArticle)
