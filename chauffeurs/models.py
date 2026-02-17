from django.db import models
from django.utils import timezone
from datetime import timedelta

class Chauffeur(models.Model):
    nom_complet = models.CharField(max_length=100, verbose_name="Nom Complet")
    telephone = models.CharField(max_length=20, unique=True, verbose_name="Téléphone")
    plaque_immatriculation = models.CharField(max_length=20, blank=True, null=True, verbose_name="Plaque")
    
    photo_permis = models.FileField(upload_to='permis/', null=True, blank=True, verbose_name="Photo du Permis")
    photo_voiture = models.FileField(upload_to='voitures/', null=True, blank=True, verbose_name="Photo de la Voiture")
    
    est_actif = models.BooleanField(default=False, verbose_name="Abonnement Actif")
    est_en_ligne = models.BooleanField(default=False, verbose_name="En Service")
    
    date_expiration = models.DateTimeField(null=True, blank=True, verbose_name="Expire le")
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chauffeur"
        verbose_name_plural = "Chauffeurs"

    def save(self, *args, **kwargs):
        if self.telephone:
            self.telephone = "".join(filter(str.isdigit, str(self.telephone)))
        if self.date_expiration and self.date_expiration < timezone.now():
            self.est_actif = False
        super().save(*args, **kwargs)

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
        return f"{self.nom_complet} ({self.telephone})"