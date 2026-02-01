from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.safestring import mark_safe

class Chauffeur(models.Model):
    # --- Informations de base ---
    nom = models.CharField(max_length=100)
    nom_complet = models.CharField(max_length=100, default="Chauffeur")
    telephone = models.CharField(max_length=20, unique=True)
    plaque_immatriculation = models.CharField(max_length=20, blank=True)
    
    # Utilisation de FileField pour éviter les dépendances système complexes sur Render
    photo_permis = models.FileField(upload_to='chauffeurs/permis/', null=True, blank=True)
    photo_voiture = models.FileField(upload_to='chauffeurs/voitures/', null=True, blank=True)
    
    # --- Statut et Abonnement ---
    est_en_ligne = models.BooleanField(default=False)
    est_actif = models.BooleanField(default=False)
    date_expiration = models.DateTimeField(null=True, blank=True)
    
    # --- Localisation ---
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} ({self.telephone})"

    # --- LOGIQUE D'ABONNEMENT ---

    def enregistrer_paiement(self):
        """Ajoute 30 jours à l'abonnement de manière intelligente."""
        self.est_actif = True
        maintenant = timezone.now()
        
        # Si déjà actif, on ajoute 30 jours à la suite
        if self.date_expiration and self.date_expiration > maintenant:
            self.date_expiration += timedelta(days=30)
        # Si expiré ou nouveau, on part de maintenant
        else:
            self.date_expiration = maintenant + timedelta(days=30)
        
        self.save()

    def verifier_statut_abonnement(self):
        """Vérifie l'expiration et coupe l'accès si nécessaire."""
        if self.date_expiration:
            if self.date_expiration < timezone.now():
                self.est_actif = False
                self.est_en_ligne = False 
            else:
                self.est_actif = True
        else:
            self.est_actif = False
            self.est_en_ligne = False
        self.save()

    def jours_restants(self):
        """Retourne le nombre de jours entiers restants."""
        if self.date_expiration and self.date_expiration > timezone.now():
            delta = self.date_expiration - timezone.now()
            return max(0, delta.days)
        return 0

    def est_vraiment_en_ligne(self):
        """Considère le chauffeur hors-ligne si pas de mise à jour GPS depuis 5 min."""
        if not self.est_en_ligne or not self.est_actif:
            return False
        seuil = timezone.now() - timedelta(minutes=5)
        return self.updated_at >= seuil

    # --- AFFICHAGE DANS L'ADMIN DJANGO ---
    def apercu_permis(self):
        if self.photo_permis:
            return mark_safe(f'<img src="{self.photo_permis.url}" width="100" style="border-radius:5px;" />')
        return "Pas de photo"
    apercu_permis.short_description = "Aperçu Permis"

    def apercu_voiture(self):
        if self.photo_voiture:
            return mark_safe(f'<img src="{self.photo_voiture.url}" width="100" style="border-radius:5px;" />')
        return "Pas de photo"
    apercu_voiture.short_description = "Aperçu Voiture"