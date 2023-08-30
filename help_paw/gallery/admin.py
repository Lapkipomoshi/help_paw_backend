from django.contrib import admin

from gallery.models import Image


class NewsAdmin(admin.ModelAdmin):
    filter_horizontal = ('gallery',)


admin.site.register(Image)
