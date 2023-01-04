from django.contrib import admin
from django.contrib.auth.models import Group

from shelters.models import Pet, Shelter, Task

admin.site.register(Pet)
admin.site.register(Shelter)
admin.site.register(Task)
admin.site.unregister(Group)
