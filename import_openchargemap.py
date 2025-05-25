import os
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Définir le module de configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EV_Charge_Maroc.settings')

# Initialiser Django
django.setup()

import requests
from stations.models import station  # Notez que nous utilisons "station" (minuscule) car c'est le nom de la classe

# Clé API OpenChargeMap from environment variable
API_KEY = os.getenv('OPENCHARGE_API_KEY')

# URL de l'API OpenChargeMap
url = "https://api.openchargemap.io/v3/poi/"

# Paramètres de la requête
params = {
    "key": API_KEY,
    "countrycode": "MA",
    "output": "json",
    "compact": False,
    "verbose": True,
    "maxresults": 500,
}

# Fonction pour récupérer toutes les stations avec pagination
def fetch_all_stations():
    all_stations = []
    page = 1
    while True:
        print(f"Récupération de la page {page}...")
        params["maxresults"] = 500
        params["offset"] = (page - 1) * 500
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Erreur lors de la requête : {response.status_code} - {response.text}")
            break
        
        data = response.json()
        if not data:
            break
        
        all_stations.extend(data)
        print(f"Nombre de stations récupérées jusqu'à présent : {len(all_stations)}")
        
        if len(data) < params["maxresults"]:
            break
        
        page += 1

    return all_stations

# Récupérer toutes les stations
stations = fetch_all_stations()

# Supprimer les anciennes stations pour éviter les doublons
station.objects.all().delete()
print("Anciennes stations supprimées.")

# Ajouter les stations dans la base de données
for station_data in stations:
    # Vérifier que la station est valide
    if not isinstance(station_data, dict):
        print(f"Station ignorée (données invalides) : {station_data}")
        continue

    # Récupérer les informations avec des valeurs par défaut
    address_info = station_data.get("AddressInfo") or {}
    nom = address_info.get("Title", "Station sans nom")
    latitude = address_info.get("Latitude")
    longitude = address_info.get("Longitude")
    adresse = address_info.get("AddressLine1", "Adresse inconnue")

    operator_info = station_data.get("OperatorInfo") or {}
    operator = operator_info.get("Title", "Opérateur inconnu")

    status_type = station_data.get("StatusType") or {}
    disponibilite = status_type.get("IsOperational", True)

    # Récupérer les types de connecteurs et la puissance
    connections = station_data.get("Connections") or []
    connector_types = ", ".join([conn.get("ConnectionType", {}).get("Title", "Inconnu") for conn in connections])
    puissance = max([conn.get('PowerKW', 0.0) for conn in connections if conn.get("PowerKW")], default=0.0)

    # Vérifier que les coordonnées sont présentes
    if latitude is None or longitude is None:
        print(f"Station ignorée (coordonnées manquantes) : {nom}")
        continue

    # Vérifier l'unicité de l'adresse
    if station.objects.filter(adresse=adresse).exists():
        print(f"Station ignorée (adresse déjà existante) : {nom}, Adresse: {adresse}")
        continue

    # Ajouter la station
    station.objects.create(
        nom=nom,
        adresse=adresse,
        latitude=latitude,
        longitude=longitude,
        disponibilite=disponibilite,
        connector_types=connector_types if connector_types else "Non spécifié",
        operator=operator,
        puissance=puissance if puissance else "Non spécifié",
        prix_kw=0.0,    # Valeur par défaut pour éviter IntegrityError
        username=None,  # Explicitement définir username à None
    )
    print(f"Ajoutée : {nom}")

print(f"Importation terminée. Total de stations importées : {station.objects.count()}")