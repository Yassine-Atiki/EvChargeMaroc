"""
URL configuration for EV_Charge_Maroc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Personnalisation de l'interface d'administration
admin.site.site_header = "EV Charge Maroc administration"
admin.site.site_title = "EV Charge Maroc administration"
admin.site.index_title = "Bienvenue dans l'administration d'EV Charge Maroc"



urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('',include('Home.urls')),
    path('stations/',include('stations.urls')),
    path('payments/', include('payments.urls')),
    path('', include('map.urls')),
    path('help/', include('help.urls')),  # Ajout de cette ligne
]

# Ajout des configurations pour servir les médias en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
