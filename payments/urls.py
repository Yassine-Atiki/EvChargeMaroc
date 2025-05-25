from django.urls import path
from django.http import HttpResponse
from .views import create_checkout_session, success_view, cancel_view, stripe_webhook

app_name = 'payments'


urlpatterns = [
    path('checkout/<int:station_id>/', create_checkout_session, name='create_checkout_session'),
    path('success/', success_view, name='success'),
    path('cancel/', cancel_view, name='cancel'),
    path('webhook/', stripe_webhook, name='webhook'),
]
