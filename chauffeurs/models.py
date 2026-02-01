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

# Création automatique de l'admin au démarrage


def gestion_admin_automatique(sender, **kwargs):
    if sender.name == 'chauffeurs':
        from django.contrib.auth.models import User
        username = 'admin'
        password = 'Parser1234'
        email = 'admin@nwele.com'
        
        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username, email, password)
                print(f"✅ Compte SUPERUSER créé : {username}")
            else:
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                print(f"🔄 Mot de passe de {username} mis à jour")
        except Exception as e:
            print(f"⚠️ Erreur lors de la gestion admin : {e}")