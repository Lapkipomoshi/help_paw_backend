from django.urls import path

from payments import views

urlpatterns = [
    path('shelters/<int:shelter_id>/donate/', views.donate, name='donate'),
    path('webhook-callback/', views.webhook_callback, name='webhook_callback'),
]
