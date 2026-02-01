from django.db import models
from django.utils import timezone
from datetime import timedelta

class Chauffeur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, unique=True)
    est_actif = models.BooleanField(default=False)
    est_en_ligne = models.BooleanField(default=False)
    date_expiration = models.DateTimeField(null=True, blank=True)

    def enregistrer_paiement(self):
        self.est_actif = True
        maintenant = timezone.now()
        if self.date_expiration and self.date_expiration > maintenant:
            self.date_expiration += timedelta(days=30)
        else:
            self.date_expiration = maintenant + timedelta(days=30)
        self.save()

    def jours_restants(self):
        if self.date_expiration and self.date_expiration > timezone.now():
            delta = self.date_expiration - timezone.now()
            return delta.days
        return 0