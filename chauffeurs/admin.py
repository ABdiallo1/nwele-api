from django.contrib import admin
from django.utils.safestring import mark_safe # Méthode plus directe
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # On garde le look C_36 intact
    list_display = ('aperçu_permis', 'aperçu_voiture', 'nom_complet', 'telephone', 'plaque_immatriculation', 'statut_service', 'statut_abonnement', 'reste')
    
    # --- RENDU DES IMAGES (ZÉRO ERREUR POSSIBLE) ---
    def aperçu_permis(self, obj):
        if obj.photo_permis:
            # mark_safe évite le problème des arguments fournis à format_html
            return mark_safe(f'<img src="{obj.photo_permis.url}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />')
        return "N/A"
    aperçu_permis.short_description = "PERMIS"

    def aperçu_voiture(self, obj):
        if obj.photo_voiture:
            return mark_safe(f'<img src="{obj.photo_voiture.url}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />')
        return "N/A"
    aperçu_voiture.short_description = "AUTO"

    # --- BADGES ET TEXTES (LOOK C_36) ---
    def statut_service(self, obj):
        color = "#28a745" if obj.est_en_ligne else "#6c757d"
        text = "EN LIGNE" if obj.est_en_ligne else "HORS LIGNE"
        return mark_safe(f'<span style="background:{color}; color:white; padding:4px 10px; border-radius:15px; font-weight:bold; font-size:10px;">{text}</span>')
    statut_service.short_description = "SERVICE"

    def statut_abonnement(self, obj):
        if obj.est_actif:
            return mark_safe('<b style="color:#28a745;">✅ ACTIF</b>')
        return mark_safe('<b style="color:#dc3545;">❌ INACTIF</b>')
    statut_abonnement.short_description = "ABONNEMENT"

    def reste(self, obj):
        if obj.date_expiration:
            diff = obj.date_expiration - timezone.now()
            days = diff.days
            return f"{days} j" if days > 0 else "Expiré"
        return "-"
    reste.short_description = "RESTE"

    # Simulation GPS pour ecran_carte.dart
    fieldsets = (
        ("Chauffeur", {'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')}),
        ("Photos", {'fields': ('photo_permis', 'photo_voiture')}),
        ("Position Simulation", {'fields': ('latitude', 'longitude')}),
        ("Statut", {'fields': ('est_actif', 'est_en_ligne', 'date_expiration')}),
    )