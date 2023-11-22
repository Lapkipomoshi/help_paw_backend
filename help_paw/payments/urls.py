from django.urls import path

from payments import views

urlpatterns = [
    path('shelters/<int:shelter_id>/donate/',
         views.donate,
         name='donate'
         ),
    path('webhook-callback/',
         views.webhook_callback,
         name='webhook_callback'
         ),
    path('get-partner-link/',
         views.partner_link,
         name='get_partner_link'
         ),
    path('partner-link-callback/',
         views.partner_link_callback,
         name='partner_link_callback'
         ),
]
