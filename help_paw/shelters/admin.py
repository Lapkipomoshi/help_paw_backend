from django.contrib import admin

from .models import Shelter, Task


@admin.site.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    pass


@admin.site.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
