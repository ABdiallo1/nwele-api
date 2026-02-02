from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # 1. Configuration des colonnes pour correspondre à C_36
    list_display = (
        'aperçu_permis', 
        'aperçu_voiture', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'statut_service', 
        'statut_abonnement', 
        'jours_restants',
        'latitude',  # Gardé pour tes simulations
        'longitude'  # Gardé pour tes simulations
    )
    
    # Rendre les coordonnées modifiables directement
    list_editable = ('latitude', 'longitude')
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')
    list_filter = ('est_actif', 'est_en_ligne')

    # --- MÉTHODES DE RENDU POUR LE LOOK C_36 ---

    def aperçu_permis(self, obj):
        if obj.photo_permis:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 4px;" />', obj.photo_permis.url)
        return "N/A"
    aperçu_permis.short_description = "PERMIS"

    def aperçu_voiture(self, obj):
        if obj.photo_voiture:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 4px;" />', obj.photo_voiture.url)
        return "N/A"
    aperçu_voiture.short_description = "AUTO"

    def statut_service(self, obj):
        if obj.est_en_ligne:
            return format_html('<span style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 15px; font-weight: bold;">EN LIGNE</span>')
        return format_html('<span style="background-color: #6c757d; color: white; padding: 5px 10px; border-radius: 15px; font-weight: bold;">HORS LIGNE</span>')
    statut_service.short_description = "SERVICE"

    def statut_abonnement(self, obj):
        if obj.est_actif:
            return format_html('<b style="color: #28a745;">✅ ACTIF</b>')
        return format_html('<b style="color: #dc3545;">❌ INACTIF</b>')
    statut_abonnement.short_description = "ABONNEMENT"

    def jours_restants(self, obj):
        if obj.date_expiration:
            diff = obj.date_expiration - timezone.now()
            days = diff.days
            if days > 0:
                return f"{days} j"
            return format_html('<span style="color: red; font-weight: bold;">Expiré</span>')
        return "-"
    jours_restants.short_description = "RESTE"

    # Configuration de la fiche détaillée (C_77)
    fieldsets = (
        ("Identité & Photos", {'fields': ('nom_complet', 'telephone', 'plaque_immatriculation', 'photo_permis', 'photo_voiture')}),
        ("Localisation (Simulations)", {'fields': ('latitude', 'longitude')}),
        ("Contrôle", {'fields': ('est_actif', 'est_en_ligne', 'date_expiration')}),
    )