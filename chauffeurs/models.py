from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User

class Chauffeur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, unique=True)
    plaque_immatriculation = models.CharField(max_length=20, blank=True)
    photo_permis = models.ImageField(upload_to='permis/', null=True, blank=True)
    photo_voiture = models.ImageField(upload_to='voitures/', null=True, blank=True)
    est_actif = models.BooleanField(default=False)
    est_en_ligne = models.BooleanField(default=False)
    date_expiration = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

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
            return (self.date_expiration - timezone.now()).days
        return 0

    def __str__(self):
        return self.nom

@receiver(post_migrate)
def create_admin_automatiquement(sender, **kwargs):
    if sender.name == 'chauffeurs': 
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@nwele.com', 'Parser1234')
            print("ADMIN CRÉÉ : admin / Parser1234")