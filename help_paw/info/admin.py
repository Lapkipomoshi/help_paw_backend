from django.contrib import admin

from info.models import (FAQ, Education, HelpArticle, News, Schedule,
                         StaticInfo, Vacancy)

admin.site.register(FAQ)
admin.site.register(News)
admin.site.register(Vacancy)
admin.site.register(StaticInfo)
admin.site.register(HelpArticle)
admin.site.register(Schedule)
admin.site.register(Education)
