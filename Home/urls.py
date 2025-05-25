from django.contrib import admin
from django.urls import path
from . import views
from .views import Home_public_page, PrivacyPolicyView, TermsOfServiceView

app_name='Home'

urlpatterns = [
    path('Home/<str:username>/',views.Home ,name='Home'),
    path('',views.Home_public_page.as_view(),name='Home'),
    path('logout/', views.logout_view, name='logout'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-of-service/', TermsOfServiceView.as_view(), name='terms_of_service'),
]