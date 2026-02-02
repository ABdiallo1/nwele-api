from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # On définit l'ordre exact des colonnes comme dans C_36 + Latitude/Longitude
    list_display = (
        'aperçu_permis', 
        'aperçu_voiture', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'statut_service', 
        'statut_abonnement', 
        'jours_restants',
        'latitude', 
        'longitude'
    )
    
    # Rend les coordonnées modifiables sans ouvrir la fiche
    list_editable = ('latitude', 'longitude')
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')
    list_filter = ('est_actif', 'est_en_ligne')

    # --- RENDU DES IMAGES (Sécurisé) ---
    def aperçu_permis(self, obj):
        if obj.photo_permis:
            return format_html('<img src="{}" width="45" height="45" style="object-fit:cover; border-radius:4px;" />', obj.photo_permis.url)
        return "N/A"
    aperçu_permis.short_description = "PERMIS"

    def aperçu_voiture(self, obj):
        if obj.photo_voiture:
            return format_html('<img src="{}" width="45" height="45" style="object-fit:cover; border-radius:4px;" />', obj.photo_voiture.url)
        return "N/A"
    aperçu_voiture.short_description = "AUTO"

    # --- BADGES DE STATUT (Look C_36) ---
    def statut_service(self, obj):
        color = "#28a745" if obj.est_en_ligne else "#6c757d"
        text = "EN LIGNE" if obj.est_en_ligne else "HORS LIGNE"
        return format_html('<span style="background:{}; color:white; padding:4px 8px; border-radius:12px; font-size:10px; font-weight:bold;">{}</span>', color, text)
    statut_service.short_description = "SERVICE"

    def statut_abonnement(self, obj):
        if obj.est_actif:
            return format_html('<span style="color:#28a745; font-weight:bold;">✅ ACTIF</span>')
        return format_html('<span style="color:#dc3545; font-weight:bold;">❌ INACTIF</span>')
    statut_abonnement.short_description = "ABONNEMENT"

    # --- CALCUL DES JOURS (Look C_36) ---
    def jours_restants(self, obj):
        if obj.date_expiration:
            diff = obj.date_expiration - timezone.now()
            jours = diff.days
            if jours > 0:
                return f"{jours} j"
            return format_html('<span style="color:#dc3545; font-weight:bold;">Expiré</span>')
        return "-"
    jours_restants.short_description = "RESTE"

    fieldsets = (
        ("Identité & Photos", {'fields': ('nom_complet', 'telephone', 'plaque_immatriculation', 'photo_permis', 'photo_voiture')}),
        ("Simulation GPS", {'fields': ('latitude', 'longitude')}),
        ("Contrôle", {'fields': ('est_actif', 'est_en_ligne', 'date_expiration')}),
    )