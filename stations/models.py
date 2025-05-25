from django.db import models
from users.models import ProprietaireVE , Fournisseur

app_name = 'stations'

class station(models.Model):
    username = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True)
    ID_Station=models.AutoField(primary_key=True)
    adresse=models.CharField(max_length=255 , unique=True)
    puissance=models.FloatField(null=True, blank=True)
    prix_kw=models.FloatField()
    disponibilite=models.BooleanField(default=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    nom = models.CharField(max_length=100, default="Station de recharge")
    connector_types = models.CharField(max_length=255, blank=True, null=True)  # Ex. "Type 2, CCS"
    operator = models.CharField(max_length=255, blank=True, null=True)  
    
import os
from django.utils import timezone

class photo(models.Model):
    ID_Station= models.ForeignKey(station, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='stations_photos/')  

class avi(models.Model):
    ID_Station= models.ForeignKey(station, related_name='avis', on_delete=models.CASCADE)
    username = models.ForeignKey(ProprietaireVE, on_delete=models.SET_NULL, null=True, blank=True)  
    commentaire = models.TextField()
    note = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Note entre 1 et 5
    date_ajout = models.DateTimeField(auto_now_add=True)


class Reservation(models.Model):
    ID_Reservation = models.AutoField(primary_key=True)
    ID_Station = models.ForeignKey(station, related_name='reservations', on_delete=models.CASCADE)
    username = models.ForeignKey(ProprietaireVE, on_delete=models.SET_NULL, null=True, blank=True)
    time_start = models.DateTimeField()  # Start time of the reservation
    duration = models.FloatField()  # Duration in hours (e.g., 0.25 for 15 minutes)
    time_end = models.DateTimeField()  # Calculated end time
    power = models.FloatField(null=True, blank=True)  # Charging power in kW
    price = models.FloatField(null=True, blank=True)  # Total price for the reservation
    paid = models.BooleanField(default=False)  # Indique si la réservation a été payée
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_formatted_id(self):
        return f"RES-{self.time_start.strftime('%Y%m%d%H')}"
    
    def get_qr_code_data(self):
        """Retourne les données à encoder dans le QR code"""
        return f"RESERVATION:{self.get_formatted_id()}|STATION:{self.ID_Station.ID_Station}|DATE:{self.time_start.strftime('%Y-%m-%d %H:%M')}|DUREE:{self.duration}"
    
    def save(self, *args, **kwargs):
        # Calculate time_end based on time_start and duration
        from datetime import timedelta
        self.time_end = self.time_start + timedelta(hours=self.duration)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation {self.ID_Reservation} at {self.ID_Station.nom} by {self.username}"