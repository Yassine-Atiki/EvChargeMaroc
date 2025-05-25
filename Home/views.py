from urllib import request
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.shortcuts import render
from django.views import View
from users.models import ProprietaireVE,Fournisseur # Import ProprietaireVE from models
from stations.models import station, Reservation
from django.db.models import Count, Avg, Sum, Q
from django.db.models.functions import ExtractYear

# Create your views here.
def Home(request,username):
    if ProprietaireVE.objects.filter(username=username).exists() :
        user = ProprietaireVE.objects.get(username=username) 
    if Fournisseur.objects.filter(username=username).exists() :
        user = Fournisseur.objects.get(username=username)

    if user and (Fournisseur.objects.filter(username=username).exists() or ProprietaireVE.objects.filter(username=username).exists()):
        return Home_user_page.as_view()(request, user)
    #else:
        #return Home_admin_page.as_view()(request)

class Home_public_page(View):
    template_name = 'Home.html'
    def get(self, request):
        # Récupérer les statistiques réelles
        stats = {
            'station_count': station.objects.count(),
            'villes_count': station.objects.values('adresse').distinct().count(),
            'users_count': ProprietaireVE.objects.count() + Fournisseur.objects.count(),
            'recharges_count': Reservation.objects.count()
        }
        
        return render(request, self.template_name, {'stats': stats})
    
class Home_user_page(View):
    template_name = 'Home.html'
    def get(self, request, user):
        # Récupérer les statistiques réelles même pour les utilisateurs connectés
        stats = {
            'station_count': station.objects.count(),
            'villes_count': station.objects.values('adresse').distinct().count(),
            'users_count': ProprietaireVE.objects.count() + Fournisseur.objects.count(),
            'recharges_count': Reservation.objects.count()
        }
        
        return render(request, self.template_name, context={'user': user, 'stats': stats})

class Home_admin_page(View):
    template_name = 'Home_Admin.html'
    def get(self, request, user):
        # Récupérer les statistiques réelles pour l'admin
        stats = {
            'station_count': station.objects.count(),
            'villes_count': station.objects.values('adresse').distinct().count(),
            'users_count': ProprietaireVE.objects.count() + Fournisseur.objects.count(),
            'recharges_count': Reservation.objects.count()
        }
        
        return render(request, self.template_name, context={'user': user, 'stats': stats})
    
def logout_view(request):
    logout(request)
    # Récupérer les statistiques réelles pour la page après déconnexion
    stats = {
        'station_count': station.objects.count(),
        'villes_count': station.objects.values('adresse').distinct().count(),
        'users_count': ProprietaireVE.objects.count() + Fournisseur.objects.count(),
        'recharges_count': Reservation.objects.count()
    }
    
    return render(request, 'Home.html', {'stats': stats})


# Ajouter ces nouvelles vues
# Ajoutez ces classes à la fin du fichier views.py
class PrivacyPolicyView(View):
    template_name = 'privacy_policy.html'
    def get(self, request):
        return render(request, self.template_name)

class TermsOfServiceView(View):
    template_name = 'terms_of_service.html'
    def get(self, request):
        return render(request, self.template_name)