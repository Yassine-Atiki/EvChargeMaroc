from django.contrib import admin
from django.urls import path
from . import views 
from .views import profile

app_name = 'users'
urlpatterns = [
    path('inscription/', views.inscription, name='inscription'),
    path('login/', views.login, name='login'),
    path('profile/<str:username>', views.profile, name='profile'),

    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/verify/<str:code>/', views.password_reset_verify, name='password_reset_verify'),
]