from django.db import models
from django.utils import timezone
from datetime import timedelta

class Chauffeur(models.Model):
    nom_complet = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, unique=True)
    plaque_immatriculation = models.CharField(max_length=20, blank=True, null=True)
    photo_permis = models.FileField(upload_to='permis/', null=True, blank=True)
    photo_voiture = models.FileField(upload_to='voitures/', null=True, blank=True)
    est_actif = models.BooleanField(default=False)
    est_en_ligne = models.BooleanField(default=False)
    date_expiration = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    def enregistrer_paiement(self):
        maintenant = timezone.now()
        if self.date_expiration and self.date_expiration > maintenant:
            self.date_expiration += timedelta(days=30)
        else:
            self.date_expiration = maintenant + timedelta(days=30)
        self.est_actif = True
        self.save()

    @property
    def jours_restants(self):
        if self.date_expiration:
            diff = self.date_expiration - timezone.now()
            return max(0, diff.days)
        return 0

    def __str__(self):
        return self.nom_complet