from PIL import Image
from django.shortcuts import redirect, render , get_object_or_404
from django.views.generic import ListView
from django.urls import reverse
from .models import station, photo, avi ,Reservation
from users.models import Fournisseur, ProprietaireVE
from django.utils import timezone
from datetime import datetime, timedelta
from .models import station, Reservation, ProprietaireVE
import qrcode
import io
from django.http import HttpResponse
from django.conf import settings  # Ajout pour STRIPE_PUBLISHABLE_KEY
from django.db.models import Sum, Avg, Count, F, FloatField
from django.db import models  # Add this import for models.functions.TruncDate
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import ExtractHour, ExtractWeekDay, TruncDate, TruncMonth
import json

class station_List_Fournisseur(ListView):
    model = station
    template_name = 'station_List_Fournisseur.html'

    def get(self, request, username, *args, **kwargs):
        # Filtrer les stations par le champ 'username' du modèle Fournisseur
        stations = station.objects.filter(username__username=username)  # Utilisez 'username__username'
        
        # Récupérer les photos et avis associés
        photos = photo.objects.filter(ID_Station__in=stations.values_list('ID_Station', flat=True))  
        avis = avi.objects.filter(ID_Station__in=stations.values_list('ID_Station', flat=True))
        
        # Calculer la note moyenne
        note = 0
        total_notes = 0
        for avis_obj in avis:
            note += avis_obj.note  # Assurez-vous que le champ 'note' existe dans le modèle 'avi'
            total_notes += 1
        
        note_moyenne = note / total_notes if total_notes > 0 else 0
        
        

        # Renvoyer les données au template
        return render(request, self.template_name, {
            'stations': stations,
            'photos': photos,
            'note': note_moyenne,
            'username': username,
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user  # Ajout de l'utilisateur au contexte
        return context

def add_station(request, username):
    F = Fournisseur.objects.get(username=username)
    if request.method == 'POST':
        adresse = request.POST.get('adresse')
        puissance = request.POST.get('puissance')
        prix_kw = request.POST.get('prix_kw')
        disponibilite = request.POST.get('disponibilite')
        photos = request.FILES.getlist('photos[]')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        nom = request.POST.get('nom')
        connector_types = request.POST.get('connector_types')
        operator = request.POST.get('operator')

        # Vérification des champs requis
        if not all([adresse, puissance, prix_kw, disponibilite, latitude, longitude, nom]):
            error = {'error': 'All fields are required.'}
            return render(request, 'ADD_Station.html', {'error': error, 'username': username})

        # Vérification du nombre de photos
        if len(photos) > 5:
            error = {'error': '⚠️ You can upload a maximum of 5 photos.'}
            return render(request, 'ADD_Station.html', {'error': error, 'username': username})

        # Vérification du format des photos
        for photo_file in photos:
            try:
                img = Image.open(photo_file)
                if img.format.lower() not in ['jpeg', 'png', 'gif']:
                    raise ValueError
            except Exception:
                error = {'error': 'Only JPEG, PNG, and GIF images are allowed.'}
                return render(request, 'ADD_Station.html', {'error': error, 'username': username})
        # Conversion des champs numériques
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            puissance = float(puissance)
            prix_kw = float(prix_kw)
        except ValueError:
            error = {'error': 'Latitude, longitude, puissance, and prix_kw must be valid numbers.'}
            return render(request, 'ADD_Station.html', {'error': error, 'username': username})

        if puissance <= 0 or prix_kw <= 0:
            error = {'error': 'Puissance and prix_kw must be positive numbers.'}
            return render(request, 'ADD_Station.html', {'error': error, 'username': username})

        # Vérification des coordonnées
        if not (27.6 <= latitude <= 35.9 and -13.0 <= longitude <= -0.9):
            error = {'error': 'This station is not in Morocco!'}
            return render(request, 'ADD_Station.html', {'error': error, 'username': username})

        # Vérification si une station avec les mêmes coordonnées existe déjà
        existing_station = station.objects.filter(latitude=latitude, longitude=longitude).first()
        if existing_station:
            if existing_station.username is None:
                # Supprimer la station existante avec username=None
                existing_station.delete()
            else:
                # Si username != None, afficher une erreur
                error = {'error': 'This station already exists.'}
                return render(request, 'ADD_Station.html', {'error': error, 'username': username})

        if station.objects.filter(adresse=adresse).exists():
            error = {'error': 'A station with this address already exists.'}
            return render(request, 'ADD_Station.html', {'error': error, 'username': username})

        # Création de la station
        new_station = station.objects.create(
            username=F,
            adresse=adresse,
            puissance=puissance,
            prix_kw=prix_kw,
            disponibilite=disponibilite,
            latitude=latitude,
            longitude=longitude,
            nom=nom,
            connector_types=connector_types,
            operator=operator
        )

        # Ajout des photos associées
        for photo_file in photos:
            photo.objects.create(
                ID_Station=new_station,
                image=photo_file
            )

        # Redirection après succès
        return redirect(reverse('stations:station_List_Fournisseur', kwargs={'username': username}))

    # Si la méthode est GET, afficher le formulaire
    return render(request, 'ADD_Station.html', {'username': username})

def delete_station(request, ID_Station, username):
        photos_delete= photo.objects.filter(ID_Station=ID_Station)
        for photo_obj in photos_delete:
            delete_photo(request,ID_Station=ID_Station, photo_id=photo_obj.id , username=username)
            
        avis_station_to_delete = avi.objects.filter(ID_Station=ID_Station)
        avis_station_to_delete.delete()

        station_to_delete = station.objects.get(ID_Station=ID_Station)
        station_to_delete.delete()

        return redirect(reverse('stations:station_List_Fournisseur', kwargs={'username':username}))

def update_station(request, ID_Station, username):
    station_update = station.objects.get(ID_Station=ID_Station, username__username=username)
    
    if request.method == 'POST':
        adresse = request.POST.get('adresse')
        puissance = request.POST.get('puissance')
        prix_kw = request.POST.get('prix_kw')
        disponibilite = request.POST.get('disponibilite')
        photos = request.FILES.getlist('photos[]')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        nom = request.POST.get('nom')

        # Vérifier des champs requis
        if not all([adresse, puissance, prix_kw, disponibilite, latitude, longitude, nom]):
            error = {'error': 'All fields are required.'}
            return render(request, 'update_station.html', {'error': error, 'station': station_update, 'username': username})

        # Conversion des champs numériques
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            puissance = float(puissance)
            prix_kw = float(prix_kw)
        except ValueError:
            error = {'error': 'Latitude, longitude, puissance, and prix_kw must be valid numbers.'}
            return render(request, 'update_station.html', {'error': error, 'station': station_update, 'username': username})

        # Vérifier des valeurs positives pour puissance et prix_kw
        if puissance <= 0 or prix_kw <= 0:
            error = {'error': 'Puissance and prix_kw must be positive numbers.'}
            return render(request, 'update_station.html', {'error': error, 'station': station_update, 'username': username})

        # Vérifier des coordonnées
        if not (27.6 <= latitude <= 35.9 and -13.0 <= longitude <= -0.9):
            error = {'error': 'This station is not in Morocco!'}
            return render(request, 'update_station.html', {'error': error, 'station': station_update, 'username': username})

        # Vérifier des doublons d'adresse
        if station.objects.filter(adresse=adresse).exclude(ID_Station=ID_Station).exists():
            error = {'error': 'A station with this address already exists.'}
            return render(request, 'update_station.html', {'error': error, 'station': station_update, 'username': username})

        # Vérifier des doublons de coordonnées
        existing_station = station.objects.filter(latitude=latitude, longitude=longitude).exclude(ID_Station=ID_Station).first()
        if existing_station:
            if existing_station.username is None:
                # Supprimer la station existante avec username=None
                existing_station.delete()
            else:
                # Si username != None, afficher une erreur
                error = {'error': 'A station with these coordinates already exists.'}
                return render(request, 'update_station.html', {'error': error, 'station': station_update, 'username': username})

        # Vérifier du nombre de photos
        if len(photos) > 5:
            error = {'error': '⚠️ You can upload a maximum of 5 photos.'}
            return render(request, 'update_station.html', {'error': error, 'station': station_update, 'username': username})

        # Vérifier du format des photos
        for photo_file in photos:
            try:
                img = Image.open(photo_file)
                if img.format.lower() not in ['jpeg', 'png', 'gif']:
                    raise ValueError
            except Exception:
                error = {'error': 'Only JPEG, PNG, and GIF images are allowed.'}
                return render(request, 'update_station.html', {'error': error, 'station': station_update, 'username': username})

        # Mise à jour de la station
        station_update.adresse = adresse
        station_update.puissance = puissance
        station_update.prix_kw = prix_kw
        station_update.disponibilite = disponibilite
        station_update.latitude = latitude
        station_update.longitude = longitude
        station_update.nom = nom

        # Mise à jour des champs supplémentaires
        station_update.connector_types = request.POST.get('connector_types')
        station_update.operator = request.POST.get('operator')
        station_update.save()

        # Ajout des nouvelles photos
        for photo_file in photos:
            photo.objects.create(
                ID_Station=station_update,
                image=photo_file
            )

        # Redirection après succès
        return redirect(reverse('stations:station_List_Fournisseur', kwargs={'username': username}))
    
    # Gérer la requête GET : afficher le formulaire pré-rempli
    return render(request, 'update_station.html', {'station': station_update, 'username': username})

def delete_photo(request, ID_Station, photo_id, username):
    # Suppression de la photo
    photo_to_delete = photo.objects.get(id=photo_id, ID_Station=ID_Station)
    photo_to_delete.delete()

    return redirect(reverse('stations:station_List_Fournisseur', kwargs={'username': username}))

def station_List_ProprietaireVE(request):
    username = request.user.username if request.user.is_authenticated else ''
    stations_list = station.objects.filter(username__isnull=False)
    
    # Récupérer les photos
    photos = photo.objects.filter(ID_Station__in=stations_list.values_list('ID_Station', flat=True))
    
    # Récupérer tous les avis
    avis_list = avi.objects.filter(ID_Station__in=stations_list.values_list('ID_Station', flat=True))
    
    # Calculer la note moyenne pour chaque station
    stations_with_ratings = []
    for station_obj in stations_list:
        # Filtrer les avis pour cette station spécifique
        station_avis = avis_list.filter(ID_Station=station_obj)
        
        # Calculer la note moyenne pour cette station
        total_notes = station_avis.count()
        if total_notes > 0:
            note_moyenne = sum(a.note for a in station_avis) / total_notes
            # Arrondir à une décimale
            note_moyenne = round(note_moyenne, 1)
        else:
            note_moyenne = 0
        
        # Ajouter la note moyenne comme attribut à l'objet station
        station_obj.note = note_moyenne
        stations_with_ratings.append(station_obj)
    
    # Récupérer l'objet utilisateur spécifique
    user = request.user
    if user.is_authenticated:
        # Vérifier d'abord si c'est un Fournisseur
        if Fournisseur.objects.filter(username=user.username).exists():
            user = Fournisseur.objects.get(username=user.username)
            # Remplacer les print de débogage par un système de logging
            import logging
            logger = logging.getLogger(__name__)
            
            # Au lieu de:
            # print(f"Utilisateur identifié comme Fournisseur: {user.username}")  # Débogage
            
            # Utiliser:
            logger.debug(f"Utilisateur identifié comme Fournisseur: {user.username}")  # Débogage
        # Sinon, vérifier si c'est un ProprietaireVE
        elif ProprietaireVE.objects.filter(username=user.username).exists():
            user = ProprietaireVE.objects.get(username=user.username)
            print(f"Utilisateur identifié comme ProprietaireVE: {user.username}")  # Débogage
    
    # Renvoyer les données au template
    return render(request, 'station_List_ProprietaireVE.html', {
        'stations': stations_with_ratings,
        'photos': photos,
        'user': user  # Utiliser l'objet utilisateur spécifique
    })


def reservations(request, ID_Station, username):
    # Récupérer la station
    station_obj = get_object_or_404(station, ID_Station=ID_Station)
    user = get_object_or_404(ProprietaireVE, username=username)

    # Photos et avis
    photos = photo.objects.filter(ID_Station=ID_Station)
    reviews = avi.objects.filter(ID_Station=ID_Station)

    # Vérifier si l'utilisateur a déjà réservé cette station
    has_reservation = Reservation.objects.filter(
        ID_Station=station_obj,
        username=user,
        time_end__lt=timezone.now()  # Réservations passées uniquement
    ).exists()

    # Vérifier si l'utilisateur a déjà laissé un avis
    user_review = None
    if has_reservation:
        user_review = avi.objects.filter(ID_Station=station_obj, username=user).first()

    # Calcul de la note moyenne
    total_notes = reviews.count()
    note_moyenne = round(sum(r.note for r in reviews) / total_notes, 1) if total_notes > 0 else 0

    # Détermination de la date courante (ou sélectionnée)
    current_date = timezone.now().date()
    date_param = request.GET.get('date')
    try:
        if date_param:
            # Correction du format de date
            current_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            print(f"Date sélectionnée: {current_date} (à partir du paramètre: {date_param})")
    except ValueError as e:
        print(f"Erreur de format de date: {e} - Paramètre reçu: {date_param}")
        pass

    # Dates précédente et suivante pour la navigation
    prev_date = current_date - timedelta(days=1)
    next_date = current_date + timedelta(days=1)
    print(f"Date actuelle: {current_date}, Précédente: {prev_date}, Suivante: {next_date}")

    # Récupérer les réservations du jour
    day_reservations = Reservation.objects.filter(
        ID_Station=station_obj,
        time_start__date=current_date
    )

    # Génération des créneaux (08:00–20:00 toutes les 15 min)
    start_hour, end_hour, interval = 8, 20, 15
    slots = []
    t = timezone.make_aware(datetime.combine(current_date, datetime.min.time()) + timedelta(hours=start_hour))

    while t.hour < end_hour:
        slot = {
            'time': t.strftime('%H:%M'),
            'available': not any(
                not ((t + timedelta(minutes=interval)) <= r.time_start or t >= r.time_end)
                for r in day_reservations
            )
        }
        slots.append(slot)
        t += timedelta(minutes=interval)

    # Séparation des créneaux
    morning_slots = [s for s in slots if 8 <= int(s['time'][:2]) < 12]
    afternoon_slots = [s for s in slots if 12 <= int(s['time'][:2]) < 16]
    evening_slots = [s for s in slots if 16 <= int(s['time'][:2]) <= 20]

    # Ajouter la date actuelle au contexte
    now = timezone.now()
    
    context = {
        'station': station_obj,
        'photos': photos,
        'reviews': reviews,
        'note_moyenne': note_moyenne,
        'time_slots': {
            'morning': morning_slots,
            'afternoon': afternoon_slots,
            'evening': evening_slots,
        },
        'current_date': current_date,
        'prev_date': prev_date,
        'next_date': next_date,
        'username': username,
        'connectors': station_obj.connector_types.split(',') if station_obj.connector_types else [],
        'has_reservation': has_reservation,
        'user_review': user_review,
        'user': user,  # Ajout pour station_details.html
        'now': now,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,  # Ajout de la clé Stripe
    }
    
    return render(request, 'station_details.html', context)


def make_reservation(request, ID_Station, username):
    if request.method == 'POST':
        station_obj = station.objects.get(ID_Station=ID_Station)
        user = ProprietaireVE.objects.get(username=username)

        try:
            time_start_str = request.POST.get('time_start')
            power = float(request.POST.get('power'))
            duration = float(request.POST.get('duration'))
        except (TypeError, ValueError):
            return render(request, 'station_details.html', {
                'station': station_obj,
                'username': username,
                'error': 'Invalid input values'
            })

        # Parse and convert time_start to aware datetime
        try:
            time_start = datetime.strptime(time_start_str, '%H:%M')
            current_date = timezone.now().date()
            if request.GET.get('date'):
                current_date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()
            time_start = timezone.make_aware(
                datetime.combine(current_date, time_start.time())
            )
        except ValueError:
            return render(request, 'station_details.html', {
                'station': station_obj,
                'error': 'Invalid time format'
            })

        # Calculate price
        price = power * duration * station_obj.prix_kw

        # Check for overlapping reservations
        time_end = time_start + timedelta(hours=duration)
        conflicting_reservations = Reservation.objects.filter(
            ID_Station=station_obj,
            time_start__lt=time_end,
            time_end__gt=time_start
        )

        if conflicting_reservations.exists():
            return redirect('stations:reservations', ID_Station=ID_Station, username=username)

        # Create reservation
        reservation = Reservation(
            ID_Station=station_obj,
            username=user,
            time_start=time_start,
            duration=duration,
            power=power,
            price=price
        )
        reservation.save()
        return redirect('stations:reservation_confirmation', reservation_id=reservation.ID_Reservation)

    # Si méthode != POST
    return redirect('stations:reservations', ID_Station=ID_Station, username=username)



def reservation_confirmation(request, reservation_id):
    reservation = get_object_or_404(Reservation, ID_Reservation=reservation_id)
    station_obj = station.objects.get(ID_Station=reservation.ID_Station.ID_Station) 
    # Process the reservation confirmation or any logic you need
    return render(request, 'reservation_confirmation.html', {'reservation': reservation, 'station': station_obj})



def generate_qr_code(request, reservation_id):
    """Génère un QR code pour une réservation spécifique"""
    try:
        reservation = Reservation.objects.get(ID_Reservation=reservation_id)
        
        # Création du QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(reservation.get_qr_code_data())
        qr.make(fit=True)

        # Création de l'image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Sauvegarde dans un buffer
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Retourne l'image
        return HttpResponse(buffer, content_type="image/png")
    except Reservation.DoesNotExist:
        return HttpResponse("Réservation non trouvée", status=404)


def user_reservations(request, username):
    """Affiche la liste des réservations d'un utilisateur"""
    # Récupérer l'utilisateur
    user = get_object_or_404(ProprietaireVE, username=username)
    
    # Récupérer toutes les réservations de l'utilisateur, triées par date (les plus récentes d'abord)
    reservations = Reservation.objects.filter(username=user).order_by('-time_start')
    
    # Regrouper les réservations par statut (à venir, passées)
    now = timezone.now()
    upcoming_reservations = []
    past_reservations = []
    
    for reservation in reservations:
        if reservation.time_start > now:
            upcoming_reservations.append(reservation)
        else:
            past_reservations.append(reservation)
    
    context = {
        'username': username,
        'upcoming_reservations': upcoming_reservations,
        'past_reservations': past_reservations,
    }
    
    return render(request, 'list_reservations.html', context)


def edit_review(request, ID_Station, username):
    if request.method == 'POST':
        station_obj = get_object_or_404(station, ID_Station=ID_Station)
        user = get_object_or_404(ProprietaireVE, username=username)
        
        # Vérifier si l'utilisateur a déjà réservé cette station
        has_reservation = Reservation.objects.filter(
            ID_Station=station_obj,
            username=user,
            time_end__lt=timezone.now()  # Réservations passées uniquement
        ).exists()
        
        if not has_reservation:
            # Rediriger avec un message d'erreur si l'utilisateur n'a pas de réservation
            return redirect(reverse('stations:reservations', kwargs={'ID_Station': ID_Station, 'username': username}))
        
        # Récupérer ou créer l'avis
        existing_review, created = avi.objects.get_or_create(
            ID_Station=station_obj,
            username=user,
            defaults={'note': 5, 'commentaire': ''}
        )
        
        # Mettre à jour l'avis
        note = request.POST.get('note')  # Corrigé: utilise 'note' au lieu de 'rating'
        commentaire = request.POST.get('commentaire')  # Corrigé: utilise 'commentaire' au lieu de 'review_text'
        
        if note and commentaire:
            existing_review.note = int(note)  # Conversion en entier pour s'assurer que c'est un nombre
            existing_review.commentaire = commentaire
            existing_review.save()
        
        # Dans la fonction edit_review, remplacer la redirection par :
        return redirect(reverse('stations:reservations', kwargs={'ID_Station': ID_Station, 'username': username}) + '#reviews-tab')
    
    # Si méthode != POST
    return redirect(reverse('stations:reservations', kwargs={'ID_Station': ID_Station, 'username': username}))

def station_statistics(request, ID_Station, username):
    # Récupération des objets
    fournisseur = get_object_or_404(Fournisseur, username=username)
    station_obj = get_object_or_404(station, ID_Station=ID_Station, username=fournisseur)
    
    # Récupérer la période sélectionnée
    period = request.GET.get('period', 'month')
    
    # Définir la plage de dates en fonction de la période
    now = timezone.now()
    if period == 'day':
        start_date = now - timedelta(days=1)
        period_label = 'dernières 24 heures'
    elif period == 'week':
        start_date = now - timedelta(days=7)
        period_label = '7 derniers jours'
    elif period == 'month':
        start_date = now - timedelta(days=30)
        period_label = '30 derniers jours'
    elif period == 'quarter':
        start_date = now - timedelta(days=90)
        period_label = '3 derniers mois'
    elif period == 'year':
        start_date = now - timedelta(days=365)
        period_label = 'dernière année'
    else:
        # Par défaut: 30 jours
        start_date = now - timedelta(days=30)
        period = 'month'
        period_label = '30 derniers jours'
    
    # Calcul des KPI
    reservations = Reservation.objects.filter(ID_Station=station_obj, time_start__gte=start_date)
    
    # Calcul des métriques principales
    total_energy = reservations.aggregate(
        total=Sum(F('power') * F('duration'), output_field=FloatField())
    )['total'] or 0
    
    total_revenue = reservations.aggregate(
        total=Sum('price', output_field=FloatField())
    )['total'] or 0
    
    total_sessions = reservations.count()
    
    avg_duration = reservations.aggregate(
        avg=Avg(F('duration') * 60)  # Conversion en minutes
    )['avg'] or 0
    
    # Calcul de la disponibilité (exemple simplifié)
    first_reservation = Reservation.objects.filter(ID_Station=station_obj).order_by('time_start').first()
    if period == 'day':
        total_hours = 24
        available_hours = reservations.annotate(
            hour=ExtractHour('time_start')
        ).values('hour').distinct().count()
        uptime_pct = round((available_hours / total_hours) * 100, 1)
    else:
        total_days = (now - start_date).days
        available_days = reservations.annotate(
            day=TruncDate('time_start')
        ).values('day').distinct().count()
        uptime_pct = round((available_days / total_days) * 100, 1) if total_days > 0 else 0

    # Données pour les graphiques
    if period == 'day':
        # Données par heure pour la journée
        daily_data = reservations.annotate(
            hour=ExtractHour('time_start')
        ).values('hour').annotate(
            sessions=Count('ID_Reservation'),
            energy=Sum(F('power') * F('duration')),
            revenue=Sum('price')
        ).order_by('hour')
        
        chart_data = {
            'days': [f"{entry['hour']}h" for entry in daily_data],
            'sessions': [entry['sessions'] for entry in daily_data],
            'energy': [float(entry['energy'] or 0) for entry in daily_data],
            'revenue': [float(entry['revenue'] or 0) for entry in daily_data],
        }
    elif period == 'week':
        # Données par jour pour la semaine
        daily_data = reservations.annotate(
            day=TruncDate('time_start')
        ).values('day').annotate(
            sessions=Count('ID_Reservation'),
            energy=Sum(F('power') * F('duration')),
            revenue=Sum('price')
        ).order_by('day')
        
        chart_data = {
            'days': [entry['day'].strftime('%d/%m') for entry in daily_data],
            'sessions': [entry['sessions'] for entry in daily_data],
            'energy': [float(entry['energy'] or 0) for entry in daily_data],
            'revenue': [float(entry['revenue'] or 0) for entry in daily_data],
        }
    elif period == 'year':
        # Données par mois pour l'année
        monthly_data = reservations.annotate(
            month=TruncMonth('time_start')
        ).values('month').annotate(
            sessions=Count('ID_Reservation'),
            energy=Sum(F('power') * F('duration')),
            revenue=Sum('price')
        ).order_by('month')
        
        chart_data = {
            'days': [entry['month'].strftime('%b %Y') for entry in monthly_data],
            'sessions': [entry['sessions'] for entry in monthly_data],
            'energy': [float(entry['energy'] or 0) for entry in monthly_data],
            'revenue': [float(entry['revenue'] or 0) for entry in monthly_data],
        }
    else:  # month ou quarter
        # Données par jour
        daily_data = reservations.annotate(
            day=TruncDate('time_start')
        ).values('day').annotate(
            sessions=Count('ID_Reservation'),
            energy=Sum(F('power') * F('duration')),
            revenue=Sum('price')
        ).order_by('day')
        
        chart_data = {
            'days': [entry['day'].strftime('%d/%m') for entry in daily_data],
            'sessions': [entry['sessions'] for entry in daily_data],
            'energy': [float(entry['energy'] or 0) for entry in daily_data],
            'revenue': [float(entry['revenue'] or 0) for entry in daily_data],
        }

    # Ajout des données pour la répartition par heure
    hourly_data = reservations.annotate(
        hour=ExtractHour('time_start')
    ).values('hour').annotate(
        count=Count('ID_Reservation')
    ).order_by('hour')

    # Ajout des données pour la répartition par jour de la semaine
    weekday_data = reservations.annotate(
        weekday=ExtractWeekDay('time_start')
    ).values('weekday').annotate(
        count=Count('ID_Reservation')
    ).order_by('weekday')

    # Compléter les données des graphiques
    chart_data.update({
        'hours': list(range(24)),
        'hourly_counts': [next((entry['count'] for entry in hourly_data if entry['hour'] == hour), 0) for hour in range(24)],
        'weekdays': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'],
        'weekday_counts': [next((entry['count'] for entry in weekday_data if entry['weekday'] == day), 0) for day in range(1, 8)],
    })

    # Convertir les données pour JavaScript
    chart_data_json = {
        'days': json.dumps(chart_data['days']),
        'sessions': json.dumps(chart_data['sessions']),
        'energy': json.dumps(chart_data['energy']),
        'revenue': json.dumps(chart_data['revenue']),
        'hours': json.dumps(chart_data['hours']),
        'hourly_counts': json.dumps(chart_data['hourly_counts']),
        'weekdays': json.dumps(chart_data['weekdays']),
        'weekday_counts': json.dumps(chart_data['weekday_counts']),
    }

    # Réservations récentes
    recent_reservations = Reservation.objects.filter(ID_Station=station_obj).select_related('username').order_by('-time_start')[:10]

    context = {
        'station': station_obj,
        'total_energy': round(total_energy, 1),
        'total_revenue': round(total_revenue, 2),
        'total_sessions': total_sessions,
        'avg_duration': round(avg_duration),
        'uptime_pct': uptime_pct,
        'recent_reservations': recent_reservations,
        'chart_data': chart_data_json,
        'period': period,
        'period_label': period_label,
        'now': now,
    }
    
    return render(request, 'station_statistique.html', context)