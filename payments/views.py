import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json

# Débogage des imports
try:
    from stations.models import station, Reservation
    print("Successfully imported station and Reservation from stations.models")
except ImportError as e:
    print(f"Failed to import from stations.models: {e}")
    raise

try:
    from users.models import ProprietaireVE
    print("Successfully imported ProprietaireVE from users.models")
except ImportError as e:
    print(f"Failed to import from users.models: {e}")
    raise

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
@login_required
def create_checkout_session(request, station_id):
    print(f"create_checkout_session called with station_id: {station_id}")
    print(f"Request method: {request.method}")
    print(f"Station ID: {station_id}")
    print(f"POST data: {request.POST}")
    print(f"Content-Type: {request.content_type}")
    
    if request.method == "POST":
        try:
            print("Inside POST block")
            # Vérifier que l'utilisateur est un ProprietaireVE
            try:
                proprietaire = ProprietaireVE.objects.get(username=request.user.username)
                print(f"Found ProprietaireVE: {proprietaire}")
            except ProprietaireVE.DoesNotExist:
                return JsonResponse({'error': 'Utilisateur non autorisé'}, status=403)

            # Récupérer la station
            selected_station = station.objects.get(ID_Station=station_id)
            print(f"Found station: {selected_station}")

            # Récupérer les données de la réservation depuis le formulaire
            # Essayez d'abord request.POST, puis request.body si nécessaire
            time_start = request.POST.get('time_start')
            duration = request.POST.get('duration')
            power = request.POST.get('power')
            
            print(f"Données extraites - time_start: {time_start}, duration: {duration}, power: {power}")
            
            # Si les données ne sont pas dans request.POST, essayez de les extraire du corps de la requête
            if not time_start or not duration or not power:
                try:
                    if 'application/json' in request.content_type:
                        body_data = json.loads(request.body.decode('utf-8'))
                        time_start = body_data.get('time_start', time_start)
                        duration = body_data.get('duration', duration)
                        power = body_data.get('power', power)
                        print(f"Données extraites du JSON - time_start: {time_start}, duration: {duration}, power: {power}")
                except Exception as e:
                    print(f"Erreur lors de l'extraction des données JSON: {str(e)}")

            if not time_start or not duration or not power:
                return JsonResponse({'error': 'Veuillez spécifier la date de début, la durée et la puissance'}, status=400)

            # Convertir en objets datetime et float
            try:
                time_start = timezone.datetime.fromisoformat(time_start.replace('Z', '+00:00'))
                duration = float(duration)
                power = float(power)
            except Exception as e:
                print(f"Erreur de conversion des données: {str(e)}")
                return JsonResponse({'error': f'Erreur de format des données: {str(e)}'}, status=400)

            # Calculer le prix
            price_per_kwh = selected_station.prix_kw if selected_station.prix_kw else 5.0
            price = power * duration * price_per_kwh

            # Vérifier les conflits de réservation
            time_end = time_start + timezone.timedelta(hours=duration)
            conflicting_reservations = Reservation.objects.filter(
                ID_Station=selected_station,
                time_start__lt=time_end,
                time_end__gt=time_start
            )
            if conflicting_reservations.exists():
                return JsonResponse({'error': 'Ce créneau est déjà réservé'}, status=409)

            # Créer une réservation
            reservation = Reservation.objects.create(
                ID_Station=selected_station,
                username=proprietaire,
                time_start=time_start,
                duration=duration,
                time_end=time_start + timezone.timedelta(hours=duration),
                power=power,
                price=price,
                paid=False
            )
            print(f"Created reservation: {reservation.ID_Reservation}")

            # Créer une session Stripe Checkout
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'mad',
                            'product_data': {
                                'name': f"Réservation - {selected_station.nom}",
                            },
                            'unit_amount': int(reservation.price * 100),
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=f'http://127.0.0.1:8000/stations/reservation/{reservation.ID_Reservation}/confirmation/',
                    cancel_url='http://127.0.0.1:8000/payments/cancel/',
                    metadata={
                        'reservation_id': reservation.ID_Reservation
                    }
                )
                print(f"Created Stripe session: {session.id}")
                return JsonResponse({'id': session.id})
            except Exception as e:
                print(f"Error creating Stripe session: {str(e)}")
                # Supprimer la réservation créée en cas d'erreur Stripe
                reservation.delete()
                return JsonResponse({'error': f'Erreur Stripe: {str(e)}'}, status=500)
        except station.DoesNotExist:
            return JsonResponse({'error': 'Station non trouvée'}, status=404)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def success_view(request):
    try:
        reservation = Reservation.objects.filter(
            username__username=request.user.username
        ).latest('created_at')
        return redirect('stations:reservation_confirmation', reservation_id=reservation.ID_Reservation)
    except Reservation.DoesNotExist:
        return render(request, 'success.html', {})

def cancel_view(request):
    try:
        # Vérifier si l'utilisateur est connecté
        if not request.user.is_authenticated:
            return render(request, 'cancel.html', {
                'error': 'Utilisateur non connecté'
            })
            
        # Tenter de récupérer la dernière réservation
        try:
            reservation = Reservation.objects.filter(
                username__username=request.user.username
            ).latest('created_at')
            
            # Vérifier si la station existe
            if reservation and reservation.ID_Station:
                return render(request, 'cancel.html', {
                    'station': reservation.ID_Station,
                    'reservation': reservation
                })
            else:
                return render(request, 'cancel.html', {
                    'error': 'Station non trouvée'
                })
                
        except Reservation.DoesNotExist:
            return render(request, 'cancel.html', {
                'error': 'Aucune réservation trouvée'
            })
    except Exception as e:
        # Log l'erreur mais renvoyer une page propre
        print(f"Erreur dans cancel_view: {str(e)}")
        return render(request, 'cancel.html', {
            'error': 'Une erreur est survenue'
        })

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'error': 'Payload invalide'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Signature invalide'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        reservation_id = session['metadata']['reservation_id']
        try:
            reservation = Reservation.objects.get(ID_Reservation=reservation_id)
            reservation.paid = True
            reservation.save()
            print(f"Réservation {reservation_id} marquée comme payée.")
        except Reservation.DoesNotExist:
            print(f"Réservation {reservation_id} non trouvée.")

    return JsonResponse({'status': 'success'}, status=200)