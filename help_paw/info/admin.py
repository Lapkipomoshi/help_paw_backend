from django.contrib import admin

from .models import Image, OwnVacancy, Vacancy


@admin.site.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass


@admin.site.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    pass


@admin.site.register(OwnVacancy)
class OwnVacancyAdmin(admin.ModelAdmin):
    pass
