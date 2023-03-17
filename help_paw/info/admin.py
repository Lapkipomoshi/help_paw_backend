from django.contrib import admin

from info.models import FAQ, HelpArticle, News, StaticInfo, Vacancy

admin.site.register(FAQ)
admin.site.register(News)
admin.site.register(Vacancy)
admin.site.register(StaticInfo)
admin.site.register(HelpArticle)
