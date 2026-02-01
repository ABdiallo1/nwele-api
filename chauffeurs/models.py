from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User

class Chauffeur(models.Model):
    # --- Informations Personnelles ---
    # On change 'nom' en 'nom_complet' pour correspondre à la base SQL sur Render
    nom_complet = models.CharField(max_length=100, verbose_name="Nom Complet")
    telephone = models.CharField(max_length=20, unique=True)
    plaque_immatriculation = models.CharField(max_length=20, blank=True, null=True)
    
    # --- Documents (Photos) ---
    photo_permis = models.FileField(upload_to='permis/', null=True, blank=True)
    photo_voiture = models.FileField(upload_to='voitures/', null=True, blank=True)
    
    # --- Statuts ---
    est_actif = models.BooleanField(default=False, verbose_name="Abonnement Actif")
    est_en_ligne = models.BooleanField(default=False, verbose_name="En ligne")
    
    # --- Abonnement ---
    date_expiration = models.DateTimeField(null=True, blank=True)
    
    # --- Localisation ---
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def enregistrer_paiement(self):
        """Active l'abonnement pour 30 jours supplémentaires"""
        self.est_actif = True
        maintenant = timezone.now()
        if self.date_expiration and self.date_expiration > maintenant:
            self.date_expiration += timedelta(days=30)
        else:
            self.date_expiration = maintenant + timedelta(days=30)
        self.save()

    def jours_restants(self):
        """Retourne le nombre de jours avant expiration"""
        if self.date_expiration and self.date_expiration > timezone.now():
            return (self.date_expiration - timezone.now()).days
        return 0

    def __str__(self):
        # On utilise nom_complet ici aussi
        return f"{self.nom_complet} - {self.telephone}"

# --- CRÉATION AUTOMATIQUE DE L'ADMIN ---

@receiver(post_migrate)
def gestion_admin_automatique(sender, **kwargs):
    if sender.name == 'chauffeurs':
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
                print(f"🔄 Admin déjà présent : {username}")
        except Exception as e:
            print(f"⚠️ Erreur admin : {e}")