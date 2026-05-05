from django.db import models

class Chauffeur(models.Model):
    nom_complet = models.CharField(max_length=150)
    telephone = models.CharField(max_length=20, unique=True)
    plaque_immatriculation = models.CharField(max_length=20, unique=True)
    modele_voiture = models.CharField(max_length=100, default="Taxi")
    
    # Stockage des images (nécessite Pillow)
    photo_voiture = models.ImageField(upload_to='chauffeurs/voitures/', null=True, blank=True)
    photo_permis = models.ImageField(upload_to='chauffeurs/permis/', null=True, blank=True)

    est_actif = models.BooleanField(default=False) # Devient True après paiement Orange
    est_en_ligne = models.BooleanField(default=False) 
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    derniere_maj = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom_complet} - {self.plaque_immatriculation}"