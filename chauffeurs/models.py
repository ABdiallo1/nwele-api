from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User

class Chauffeur(models.Model):
    nom_complet = models.CharField(max_length=100, verbose_name="Nom Complet")
    telephone = models.CharField(max_length=20, unique=True)
    plaque_immatriculation = models.CharField(max_length=20, blank=True, null=True)
    
    photo_permis = models.FileField(upload_to='permis/', null=True, blank=True)
    photo_voiture = models.FileField(upload_to='voitures/', null=True, blank=True)
    
    est_actif = models.BooleanField(default=False, verbose_name="Abonnement Actif")
    est_en_ligne = models.BooleanField(default=False, verbose_name="En ligne")
    
    date_expiration = models.DateTimeField(null=True, blank=True)
    
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def enregistrer_paiement(self):
        """Active ou prolonge l'abonnement pour 30 jours"""
        maintenant = timezone.now()
        if self.date_expiration and self.date_expiration > maintenant:
            self.date_expiration += timedelta(days=30)
        else:
            self.date_expiration = maintenant + timedelta(days=30)
        self.est_actif = True
        self.save()

    @property
    def jours_restants(self):
        """Calcule le nombre de jours restants sans conflit avec est_actif"""
        if self.date_expiration and self.date_expiration > timezone.now():
            diff = self.date_expiration - timezone.now()
            return diff.days
        return 0

    def __str__(self):
        return f"{self.nom_complet} - {self.telephone}"

@receiver(post_migrate)
def gestion_admin_automatique(sender, **kwargs):
    if sender.name == 'chauffeurs':
        username, password, email = 'admin', 'Parser1234', 'admin@nwele.com'
        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username, email, password)
                print(f"✅ Super-utilisateur créé")
        except Exception as e:
            print(f"⚠️ Erreur setup admin : {e}")