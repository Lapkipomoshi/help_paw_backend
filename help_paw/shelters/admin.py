from django.contrib import admin
from django.contrib.auth.models import Group

from shelters.models import AnimalType, Pet, Shelter, Task

admin.site.register(Pet)
admin.site.register(Shelter)
admin.site.register(Task)
admin.site.register(AnimalType)

admin.site.unregister(Group)
