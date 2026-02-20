from django.db import models

class Chauffeur(models.Model):
    nom_complet = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20, unique=True)
    plaque_immatriculation = models.CharField(max_length=50)
    
    # upload_to définit le sous-dossier dans 'media/'
    photo_permis = models.FileField(upload_to='permis/', null=True, blank=True)
    photo_vehicule = models.FileField(upload_to='vehicules/', null=True, blank=True)
    
    est_actif = models.BooleanField(default=False)
    est_en_ligne = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True, default=0.0)
    longitude = models.FloatField(null=True, blank=True, default=0.0)
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom_complet