from django.contrib import admin

from payments.models import Payment, YookassaOAuthToken

admin.site.register(YookassaOAuthToken)
admin.site.register(Payment)
