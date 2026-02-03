from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User

class Chauffeur(models.Model):
    # --- Informations Personnelles ---
    # Note: 'nom_complet' remplace 'nom' pour plus de clarté
    nom_complet = models.CharField(max_length=100, verbose_name="Nom Complet")
    telephone = models.CharField(max_length=20, unique=True)
    plaque_immatriculation = models.CharField(max_length=20, blank=True, null=True)
    
    # --- Documents (Photos) ---
    # On utilise FileField pour éviter la dépendance Pillow (plus stable pour le déploiement)
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
        """Active ou prolonge l'abonnement pour 30 jours"""
        self.est_actif = True
        maintenant = timezone.now()
        if self.date_expiration and self.date_expiration > maintenant:
            self.date_expiration += timedelta(days=30)
        else:
            self.date_expiration = maintenant + timedelta(days=30)
        self.save()

    @property
    def jours_restants(self):
        """Calcule le nombre de jours restants (utilisé par l'API)"""
        if self.date_expiration and self.date_expiration > timezone.now():
            diff = self.date_expiration - timezone.now()
            return diff.days
        return 0

    def __str__(self):
        return f"{self.nom_complet} - {self.telephone}"

# --- AUTOMATISATION ADMIN & SETUP ---

@receiver(post_migrate)
def gestion_admin_automatique(sender, **kwargs):
    """Crée l'admin automatiquement après chaque migration sur Render"""
    if sender.name == 'chauffeurs':
        username = 'admin'
        password = 'Parser1234'
        email = 'admin@nwele.com'
        
        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username, email, password)
                print(f"✅ Super-utilisateur créé : {username}")
            else:
                # On s'assure que le mot de passe est toujours le bon
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                print(f"🔄 Admin mis à jour.")
        except Exception as e:
            print(f"⚠️ Erreur lors du setup admin : {e}")