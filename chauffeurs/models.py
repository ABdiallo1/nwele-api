from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User

class Chauffeur(models.Model):
    # --- Informations Personnelles ---
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, unique=True)
    plaque_immatriculation = models.CharField(max_length=20, blank=True)
    
    # --- Documents (Photos) ---
    # Ces fichiers seront stockés dans le dossier /media/ sur Render
    photo_permis = models.ImageField(upload_to='permis/', null=True, blank=True)
    photo_voiture = models.ImageField(upload_to='voitures/', null=True, blank=True)
    
    # --- Statuts ---
    est_actif = models.BooleanField(default=False, help_text="Coché si l'abonnement est payé")
    est_en_ligne = models.BooleanField(default=False, help_text="Si le chauffeur est prêt à recevoir des courses")
    
    # --- Abonnement ---
    date_expiration = models.DateTimeField(null=True, blank=True)
    
    # --- Localisation (Pour la carte Flutter) ---
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def enregistrer_paiement(self):
        """Ajoute 30 jours d'abonnement lors d'un paiement réussi"""
        self.est_actif = True
        maintenant = timezone.now()
        if self.date_expiration and self.date_expiration > maintenant:
            self.date_expiration += timedelta(days=30)
        else:
            self.date_expiration = maintenant + timedelta(days=30)
        self.save()

    def jours_restants(self):
        """Calcul le nombre de jours avant expiration"""
        if self.date_expiration and self.date_expiration > timezone.now():
            delta = self.date_expiration - timezone.now()
            return delta.days
        return 0

    def __str__(self):
        return f"{self.nom} ({self.telephone})"

# --- AUTOMATISATION DE L'ADMIN (Indispensable pour Render Gratuit) ---
@receiver(post_migrate)
def gestion_admin_automatique(sender, **kwargs):
    """
    Crée le super-utilisateur admin si absent, 
    ou réinitialise son mot de passe s'il existe déjà.
    """
    if sender.name == 'chauffeurs':
        username = 'admin'
        email = 'admin@nwele.com'
        password = 'Parser1234'
        
        user, created = User.objects.get_or_create(username=username)
        
        if created:
            user.set_password(password)
            user.email = email
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print(f"✅ ADMIN CRÉÉ : Login: {username} | Pass: {password}")
        else:
            user.set_password(password)
            user.save()
            print(f"🔄 ADMIN RÉINITIALISÉ : Login: {username} | Pass: {password}")