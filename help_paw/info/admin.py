from django.contrib import admin

from info.models import FAQ, News, OwnVacancy, StaticInfo, Vacancy

admin.site.register(FAQ)
admin.site.register(News)
admin.site.register(OwnVacancy)
admin.site.register(StaticInfo)
admin.site.register(Vacancy)
