from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login as auth_login
from django.contrib import messages
from users.models import ProprietaireVE, Fournisseur, Users
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetCode
from django.utils import timezone
from datetime import timedelta
import random
import string


def inscription(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_type == 'proprietaire':
            view = ProprietaireVE_View_creat.as_view()
            return view(request)
        elif user_type == 'fournisseur':
            view = Fournisseur_View_creat.as_view()
            return view(request)

    return render(request, 'inscription.html')

class ProprietaireVE_View_creat(CreateView):
    model = ProprietaireVE
    fields = ['CIN', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'password']
    template_name = 'inscription.html'
    success_url = '/users/login/'  # Redirect to the login page after successful registration

    def post(self, request, *args, **kwargs):
        # Récupération des données du formulaire
        CIN = request.POST.get('CIN')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')
        terms = request.POST.get('terms')

        # Créer un dictionnaire de contexte pour stocker les erreurs et les valeurs soumises
        context = {
            'form': {
                'CIN': {'value': CIN, 'errors': []},
                'first_name': {'value': first_name, 'errors': []},
                'last_name': {'value': last_name, 'errors': []},
                'username': {'value': username, 'errors': []},
                'email': {'value': email, 'errors': []},
                'phone_number': {'value': phone_number, 'errors': []},
                'password': {'value': '', 'errors': []},
                'password_confirmation': {'value': '', 'errors': []},
                'terms': {'value': terms, 'errors': []},
                'non_field_errors': []
            }
        }

        # Vérifier si un champ est vide 
        has_error = False
        
        if not terms:
            context['form']['terms']['errors'].append("Vous devez accepter les conditions d'utilisation.")
            has_error = True

        if not all([CIN, first_name, last_name, username, email, phone_number, password, password_confirmation]):
            context['form']['non_field_errors'].append("Veuillez remplir tous les champs.")
            has_error = True
            
            # Vérifier chaque champ individuellement pour afficher des erreurs spécifiques
            if not CIN:
                context['form']['CIN']['errors'].append("Ce champ est obligatoire.")
            if not first_name:
                context['form']['first_name']['errors'].append("Ce champ est obligatoire.")
            if not last_name:
                context['form']['last_name']['errors'].append("Ce champ est obligatoire.")
            if not username:
                context['form']['username']['errors'].append("Ce champ est obligatoire.")
            if not email:
                context['form']['email']['errors'].append("Ce champ est obligatoire.")
            if not phone_number:
                context['form']['phone_number']['errors'].append("Ce champ est obligatoire.")
            if not password:
                context['form']['password']['errors'].append("Ce champ est obligatoire.")
            if not password_confirmation:
                context['form']['password_confirmation']['errors'].append("Ce champ est obligatoire.")
        
        # Vérifier si les mots de passe correspondent
        if password != password_confirmation:
            context['form']['password_confirmation']['errors'].append("Les mots de passe ne correspondent pas.")
            has_error = True
        
        # Vérifier si le CIN existe déjà
        if ProprietaireVE.objects.filter(CIN=CIN).exists() or Fournisseur.objects.filter(CIN=CIN).exists():
            context['form']['CIN']['errors'].append("Ce CIN est déjà utilisé.")
            has_error = True

        # Vérifier si l'email existe déjà
        if ProprietaireVE.objects.filter(email=email).exists() or Fournisseur.objects.filter(email=email).exists():
            context['form']['email']['errors'].append("Cette adresse email est déjà utilisée.")
            has_error = True

        # Vérifier si le numéro de téléphone existe déjà
        if ProprietaireVE.objects.filter(phone_number=phone_number).exists() or Fournisseur.objects.filter(phone_number=phone_number).exists():
            context['form']['phone_number']['errors'].append("Ce numéro de téléphone est déjà utilisé.")
            has_error = True

        # Vérifier si le nom d'utilisateur existe déjà
        if ProprietaireVE.objects.filter(username=username).exists() or Fournisseur.objects.filter(username=username).exists():
            context['form']['username']['errors'].append("Ce nom d'utilisateur est déjà utilisé.")
            has_error = True
        
        if has_error:
            # S'il y a des erreurs, retourner le formulaire avec les erreurs
            return render(request, self.template_name, context)
        
        # Créer l'utilisateur
        ProprietaireVE.objects.create(
            CIN=CIN,
            first_name=first_name, 
            last_name=last_name,
            username=username,
            email=email,
            phone_number=phone_number,
            password=make_password(password)
        )
        
        messages.success(request, "Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.")
        return HttpResponseRedirect(self.success_url)

class Fournisseur_View_creat(CreateView):
    model = Fournisseur
    fields = ['CIN', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'password']
    template_name = 'inscription.html'
    success_url = '/users/login/'  # Redirect to the login page after successful registration

    def post(self, request, *args, **kwargs):
        # Récupération des données du formulaire
        CIN = request.POST.get('CIN')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')
        terms = request.POST.get('terms')

        # Créer un dictionnaire de contexte pour stocker les erreurs et les valeurs soumises
        context = {
            'form': {
                'CIN': {'value': CIN, 'errors': []},
                'first_name': {'value': first_name, 'errors': []},
                'last_name': {'value': last_name, 'errors': []},
                'username': {'value': username, 'errors': []},
                'email': {'value': email, 'errors': []},
                'phone_number': {'value': phone_number, 'errors': []},
                'password': {'value': '', 'errors': []},
                'password_confirmation': {'value': '', 'errors': []},
                'terms': {'value': terms, 'errors': []},
                'non_field_errors': []
            }
        }

        # Vérifier si un champ est vide
        has_error = False
        
        if not terms:
            context['form']['terms']['errors'].append("Vous devez accepter les conditions d'utilisation.")
            has_error = True

        if not all([CIN, first_name, last_name, username, email, phone_number, password, password_confirmation]):
            context['form']['non_field_errors'].append("Veuillez remplir tous les champs.")
            has_error = True
            
            # Vérifier chaque champ individuellement pour afficher des erreurs spécifiques
            if not CIN:
                context['form']['CIN']['errors'].append("Ce champ est obligatoire.")
            if not first_name:
                context['form']['first_name']['errors'].append("Ce champ est obligatoire.")
            if not last_name:
                context['form']['last_name']['errors'].append("Ce champ est obligatoire.")
            if not username:
                context['form']['username']['errors'].append("Ce champ est obligatoire.")
            if not email:
                context['form']['email']['errors'].append("Ce champ est obligatoire.")
            if not phone_number:
                context['form']['phone_number']['errors'].append("Ce champ est obligatoire.")
            if not password:
                context['form']['password']['errors'].append("Ce champ est obligatoire.")
            if not password_confirmation:
                context['form']['password_confirmation']['errors'].append("Ce champ est obligatoire.")
        
        # Vérifier si les mots de passe correspondent
        if password != password_confirmation:
            context['form']['password_confirmation']['errors'].append("Les mots de passe ne correspondent pas.")
            has_error = True
                
        # Vérifier si le CIN existe déjà
        if Fournisseur.objects.filter(CIN=CIN).exists() or ProprietaireVE.objects.filter(CIN=CIN).exists():
            context['form']['CIN']['errors'].append("Ce CIN est déjà utilisé.")
            has_error = True

        # Vérifier si l'email existe déjà
        if Fournisseur.objects.filter(email=email).exists() or ProprietaireVE.objects.filter(email=email).exists():
            context['form']['email']['errors'].append("Cette adresse email est déjà utilisée.")
            has_error = True

        # Vérifier si le numéro de téléphone existe déjà
        if Fournisseur.objects.filter(phone_number=phone_number).exists() or ProprietaireVE.objects.filter(phone_number=phone_number).exists():
            context['form']['phone_number']['errors'].append("Ce numéro de téléphone est déjà utilisé.")
            has_error = True

        # Vérifier si le nom d'utilisateur existe déjà
        if Fournisseur.objects.filter(username=username).exists() or ProprietaireVE.objects.filter(username=username).exists():
            context['form']['username']['errors'].append("Ce nom d'utilisateur est déjà utilisé.")
            has_error = True
        
        if has_error:
            # S'il y a des erreurs, retourner le formulaire avec les erreurs
            return render(request, self.template_name, context)
        
        # Créer l'utilisateur
        Fournisseur.objects.create(
            CIN=CIN,
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            phone_number=phone_number,
            password=make_password(password)
        )
        
        messages.success(request, "Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.")
        return HttpResponseRedirect(self.success_url)
    
# Login part for the users
def login(request):
    if request.method == 'GET':
        # Ajouter un paramètre pour rediriger vers l'admin si nécessaire
        next_url = request.GET.get('next', '')
        return render(request, 'login.html', {'next': next_url})
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')
        
        # Vérifier si c'est un superuser (admin Django)
        from django.contrib.auth import authenticate
        admin_user = authenticate(username=email, password=password)
        
        if admin_user and admin_user.is_superuser:
            auth_login(request, admin_user)
            # Rediriger vers l'admin ou la page demandée
            if next_url and next_url.startswith('/admin'):
                return HttpResponseRedirect(next_url)
            return HttpResponseRedirect('/admin/')
        
        # Continuer avec la logique existante pour les utilisateurs normaux
        user_type = request.POST.get('user_type')
        if user_type == 'proprietaire':
            view = ProprietaireVE_View_login.as_view()
            return view(request)
        elif user_type == 'fournisseur':
            view = Fournisseur_View_login.as_view()
            return view(request)
    return render(request, 'login.html')

class ProprietaireVE_View_login(LoginView):
    model = ProprietaireVE
    fields = ['email', 'password']
    template_name = 'login.html'
    
    def post(self, request, *args, **kwargs):
        # Récupération des données du formulaire
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Créer un dictionnaire de contexte pour stocker les erreurs
        context = {
            'form': {
                'email': {'value': email, 'errors': []},
                'password': {'value': '', 'errors': []},
                'non_field_errors': []
            }
        }
        
        # Vérifier si un champ est vide
        has_error = False
        
        if not all([email, password]):
            context['form']['non_field_errors'].append("Veuillez remplir tous les champs.")
            has_error = True
            
            # Vérifier chaque champ individuellement
            if not email:
                context['form']['email']['errors'].append("Ce champ est obligatoire.")
            if not password:
                context['form']['password']['errors'].append("Ce champ est obligatoire.")
        
        if not has_error:
            if ProprietaireVE.objects.filter(email=email).exists():
                user = ProprietaireVE.objects.get(email=email)
                if user.check_password(password):
                    auth_login(request, user)
                    messages.success(request, f"Bienvenue, {user.first_name} !")
                    return HttpResponseRedirect(reverse('Home:Home', args=[user.username]))
                else:
                    context['form']['password']['errors'].append("Mot de passe incorrect.")
                    has_error = True
            else:
                context['form']['email']['errors'].append("Aucun compte propriétaire trouvé avec cet email.")
                has_error = True
        
        if has_error:
            return render(request, self.template_name, context)

class Fournisseur_View_login(LoginView):
    model = Fournisseur
    fields = ['email', 'password']
    template_name = 'login.html'

    def post(self, request, *args, **kwargs):
        # Récupération des données du formulaire
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Créer un dictionnaire de contexte pour stocker les erreurs
        context = {
            'form': {
                'email': {'value': email, 'errors': []},
                'password': {'value': '', 'errors': []},
                'non_field_errors': []
            }
        }
        
        # Vérifier si un champ est vide
        has_error = False
        
        if not all([email, password]):
            context['form']['non_field_errors'].append("Veuillez remplir tous les champs.")
            has_error = True
            
            # Vérifier chaque champ individuellement
            if not email:
                context['form']['email']['errors'].append("Ce champ est obligatoire.")
            if not password:
                context['form']['password']['errors'].append("Ce champ est obligatoire.")
        
        if not has_error:
            if Fournisseur.objects.filter(email=email).exists():
                user = Fournisseur.objects.get(email=email)
                if user.check_password(password):
                    auth_login(request, user)
                    messages.success(request, f"Bienvenue, {user.first_name} !")
                    return HttpResponseRedirect(reverse('Home:Home', args=[user.username]))
                else:
                    context['form']['password']['errors'].append("Mot de passe incorrect.")
                    has_error = True
            else:
                context['form']['email']['errors'].append("Aucun compte fournisseur trouvé avec cet email.")
                has_error = True
        
        if has_error:
            return render(request, self.template_name, context)

def profile(request, username):
    # Récupérer l'utilisateur en fonction du type
    if ProprietaireVE.objects.filter(username=username).exists():
        user = ProprietaireVE.objects.get(username=username)
        user_type = "Propriétaire De Véhicule Électrique"
    elif Fournisseur.objects.filter(username=username).exists():
        user = Fournisseur.objects.get(username=username)
        user_type = "Fournisseur De Stations De Recharge"
    else:
        return render(request, 'profile.html', {'error': "Utilisateur introuvable."})

    error = None
    success = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_info':
            # Mettre à jour les informations personnelles
            CIN = request.POST.get('CIN', user.CIN)  # Utiliser la valeur actuelle si non fournie
            first_name = request.POST.get('first_name', user.first_name)
            last_name = request.POST.get('last_name', user.last_name)
            new_username = request.POST.get('username', user.username)
            email = request.POST.get('email', user.email)
            phone_number = request.POST.get('phone_number', user.phone_number)

            # Vérifier les conflits avec d'autres utilisateurs
            if email != user.email and (ProprietaireVE.objects.filter(email=email).exists() or Fournisseur.objects.filter(email=email).exists()):
                error = "L'email existe déjà."
            elif phone_number != user.phone_number and (ProprietaireVE.objects.filter(phone_number=phone_number).exists() or Fournisseur.objects.filter(phone_number=phone_number).exists()):
                error = "Le numéro de téléphone existe déjà."
            elif new_username != user.username and (ProprietaireVE.objects.filter(username=new_username).exists() or Fournisseur.objects.filter(username=new_username).exists()):
                error = "Le nom d'utilisateur existe déjà."
            else:
                # Mettre à jour les informations personnelles
                user.CIN = CIN
                user.first_name = first_name
                user.last_name = last_name
                user.username = new_username
                user.email = email
                user.phone_number = phone_number
                user.save()
                success = "Informations mises à jour avec succès."

        elif action == 'update_password':
            # Mettre à jour le mot de passe
            last_password = request.POST.get('last_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not all([last_password, new_password, confirm_password]):
                error = "Veuillez remplir tous les champs."
            elif not user.check_password(last_password):
                error = "Le mot de passe actuel est incorrect."
            elif new_password != confirm_password:
                error = "Le nouveau mot de passe et la confirmation ne correspondent pas."
            else:
                user.password = make_password(new_password)
                user.save()
                success = "Mot de passe mis à jour avec succès."

    return render(request, 'profile.html', {'user': user, 'user_type': user_type, 'error': error, 'success': success})




def generate_code(length=6):
    """Générer un code aléatoire à 6 chiffres"""
    return ''.join(random.choices(string.digits, k=length))

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = Users.objects.get(email=email)  # Utiliser Users au lieu de User
            # Générer un code de récupération
            code = generate_code()
            expires_at = timezone.now() + timedelta(minutes=30)  # Code valide 30 minutes

            # Supprimer les anciens codes pour cet utilisateur
            PasswordResetCode.objects.filter(user=user).delete()

            # Enregistrer le nouveau code
            PasswordResetCode.objects.create(
                user=user,
                code=code,
                expires_at=expires_at
            )

            # Envoyer l'email avec le code
            subject = "Récupération de mot de passe - EV Charge Maroc"
            message = f"""Bonjour {user.username},

Votre lien de réinitialisation de mot de passe est disponible. Veuillez utiliser ce code pour vérifier votre identité :

Code : {code}

Ce code est valide pendant 30 minutes.

Pour réinitialiser votre mot de passe :
1. Entrez ce code à 6 chiffres sur la page de vérification
2. Sur la page suivante, créez un nouveau mot de passe d'au moins 8 caractères

Cordialement,
L'équipe EV Charge Maroc"""
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            # Rediriger vers une page pour entrer le code
            return redirect('users:password_reset_verify', code=code)
        except Users.DoesNotExist:  # Utiliser Users au lieu de User
            return render(request, 'password_reset.html', {'error': 'Aucun utilisateur avec cet email.'})
    return render(request, 'password_reset.html')

def password_reset_verify(request, code):

    context = {}
    
    # Vérifie d'abord si le code existe dans l'URL
    try:
        reset_code_obj = PasswordResetCode.objects.get(code=code)
        if reset_code_obj.is_expired():
            reset_code_obj.delete()
            return render(request, 'password_reset_verify.html', {'error': 'Ce code a expiré. Veuillez demander un nouveau code.'})
    except PasswordResetCode.DoesNotExist:
        return render(request, 'password_reset_verify.html', {'error': 'Code de vérification invalide. Veuillez vérifier votre email ou demander un nouveau code.'})
    
    # Traitement du formulaire POST
    if request.method == "POST":
        step = request.POST.get('step')
        
        # Étape 1: Vérification du code saisi par l'utilisateur
        if step == 'verify_code':
            verification_code = request.POST.get('verification_code')
            
            # Vérifie si le code saisi correspond au code dans l'URL
            if verification_code == code:
                # Code vérifié, afficher le formulaire de réinitialisation du mot de passe
                context['code_verified'] = True
                context['verified_code'] = code
            else:
                context['error'] = 'Code de vérification incorrect. Veuillez vérifier et réessayer.'
        
        # Étape 2: Réinitialisation du mot de passe
        elif step == 'reset_password':
            verified_code = request.POST.get('verified_code')
            
            # Vérifier à nouveau que le code est valide
            try:
                reset_code = PasswordResetCode.objects.get(code=verified_code)
                if reset_code.is_expired():
                    reset_code.delete()
                    return render(request, 'password_reset_verify.html', {'error': 'Ce code a expiré. Veuillez demander un nouveau code.'})
                
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                
                # Vérifier si le mot de passe est assez long
                if len(new_password) < 8:
                    context['code_verified'] = True
                    context['verified_code'] = verified_code
                    context['error'] = 'Le mot de passe doit comporter au moins 8 caractères.'
                    return render(request, 'password_reset_verify.html', context)
                
                # Vérifier si les mots de passe correspondent
                if new_password != confirm_password:
                    context['code_verified'] = True
                    context['verified_code'] = verified_code
                    context['error'] = 'Les mots de passe ne correspondent pas.'
                    return render(request, 'password_reset_verify.html', context)
                
                # Mettre à jour le mot de passe
                user = reset_code.user
                user.set_password(new_password)
                user.save()
                
                # Supprimer le code après utilisation
                reset_code.delete()
                
                # Message de succès et redirection
                messages.success(request, 'Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.')
                return redirect('users:login')
                
            except PasswordResetCode.DoesNotExist:
                return render(request, 'password_reset_verify.html', {'error': 'Code de vérification invalide. Veuillez vérifier votre email ou demander un nouveau code.'})
    
    # Par défaut, afficher la première étape (vérification du code)
    if 'code_verified' not in context:
        context['code_verified'] = False
    
    return render(request, 'password_reset_verify.html', context)