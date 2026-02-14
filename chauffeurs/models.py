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

    def save(self, *args, **kwargs):
        # Nettoyage automatique : on ne garde que les chiffres avant de sauvegarder
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
            maintenant = timezone.now()
            if self.date_expiration > maintenant:
                diff = self.date_expiration - maintenant
                return diff.days
            else:
                # Mise à jour automatique si expiré
                if self.est_actif:
                    self.est_actif = False
                    # On évite la boucle infinie dans save() en utilisant update
                    Chauffeur.objects.filter(id=self.id).update(est_actif=False)
        return 0

    def __str__(self):
        return f"{self.nom_complet} - {self.telephone}"

@receiver(post_migrate)
def gestion_admin_automatique(sender, **kwargs):
    if sender.name == 'votre_nom_d_application': # Remplace par le nom de ton app
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@nwele.com', 'Parser1234')