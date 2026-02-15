from django.db import models
from django.utils import timezone
from datetime import timedelta

class Chauffeur(models.Model):
    nom_complet = models.CharField(max_length=100, verbose_name="Nom Complet")
    telephone = models.CharField(max_length=20, unique=True, verbose_name="Téléphone")
    plaque_immatriculation = models.CharField(max_length=20, blank=True, null=True, verbose_name="Plaque")
    
    photo_permis = models.FileField(upload_to='permis/', null=True, blank=True)
    photo_voiture = models.FileField(upload_to='voitures/', null=True, blank=True)
    
    est_actif = models.BooleanField(default=False, verbose_name="Abonnement Actif")
    est_en_ligne = models.BooleanField(default=False, verbose_name="En ligne (Service)")
    date_expiration = models.DateTimeField(null=True, blank=True, verbose_name="Date d'expiration")
    
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.telephone:
            # Garde uniquement les chiffres pour éviter les erreurs de recherche
            self.telephone = "".join(filter(str.isdigit, str(self.telephone)))
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

    class Meta:
        verbose_name = "Chauffeur"
        verbose_name_plural = "Chauffeurs"