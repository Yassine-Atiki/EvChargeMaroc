from django.http import JsonResponse
from django.shortcuts import render
from stations.models import station
from users.models import Fournisseur, ProprietaireVE  # Ajouter cette ligne

def map_view(request):
    if request.method == "POST":
        try:
            user_lat = float(request.POST.get('lat'))
            user_lon = float(request.POST.get('lon'))
            print(f"Position de l'utilisateur : lat={user_lat}, lon={user_lon}")
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Coordonnées invalides'}, status=400)

        stations = station.objects.all()
        print(f"Nombre total de stations récupérées : {stations.count()}")

        all_stations = []
        for s in stations:
            if s.latitude is None or s.longitude is None:
                print(f"Station ignorée (coordonnées manquantes) : {s.nom}")
                continue
            try:
                lat = float(s.latitude)
                lng = float(s.longitude)
                if lat < -90 or lat > 90 or lng < -180 or lng > 180:
                    print(f"Station ignorée (coordonnées hors limites) : {s.nom}, latitude={lat}, longitude={lng}")
                    continue
            except (ValueError, TypeError):
                print(f"Station ignorée (coordonnées invalides) : {s.nom}, latitude={s.latitude}, longitude={s.longitude}")
                continue
            available = bool(s.disponibilite) if s.disponibilite is not None else True
            all_stations.append({
                'name': s.nom if s.nom else "Nom inconnu",
                'lat': s.latitude,
                'lng': s.longitude,
                'address': s.adresse if s.adresse else "Adresse inconnue",
                'connector_types': s.connector_types if s.connector_types else "Non spécifié",
                'puissance': f"{s.puissance} kW" if s.puissance is not None and s.puissance > 0 else "Non spécifié",
                'operator': s.operator if s.operator else "Opérateur inconnu",
                'available': bool(s.disponibilite),
                'has_username': s.username is not None
            })
            print(f"Station ajoutée : {s.nom}, lat={lat}, lng={lng}, available={available}, has_username={s.username is not None}")

        print(f"Nombre total de stations valides : {len(all_stations)}")
        return JsonResponse({'stations': all_stations})

    # Assurez-vous que l'utilisateur est correctement transmis au template
    # Récupérer l'objet utilisateur spécifique au lieu de request.user
    user = request.user
    if user.is_authenticated:
        if Fournisseur.objects.filter(username=user.username).exists():
            user = Fournisseur.objects.get(username=user.username)
        elif ProprietaireVE.objects.filter(username=user.username).exists():
            user = ProprietaireVE.objects.get(username=user.username)
    
    return render(request, 'map.html', {'user': user})