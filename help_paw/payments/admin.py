from django.contrib import admin

from payments.models import Donation, YookassaOAuthToken

admin.site.register(YookassaOAuthToken)
admin.site.register(Donation)
