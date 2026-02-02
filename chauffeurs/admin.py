from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # 1. Configuration de l'affichage (Exactement C_36)
    list_display = (
        'aperçu_permis', 
        'aperçu_voiture', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'statut_service', 
        'statut_abonnement', 
        'temps_restant'
    )
    
    # On rend les infos de base modifiables rapidement
    list_editable = ('nom_complet', 'telephone')
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')
    list_filter = ('est_actif', 'est_en_ligne')

    # --- 2. FONCTIONS DE RENDU (SÉCURITÉ MAXIMALE) ---

    def aperçu_permis(self, obj):
        try:
            if obj.photo_permis and hasattr(obj.photo_permis, 'url'):
                return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px; border:1px solid #ddd;" />', obj.photo_permis.url)
        except:
            pass
        return "Pas de photo"
    aperçu_permis.short_description = "PERMIS"

    def aperçu_voiture(self, obj):
        try:
            if obj.photo_voiture and hasattr(obj.photo_voiture, 'url'):
                return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px; border:1px solid #ddd;" />', obj.photo_voiture.url)
        except:
            pass
        return "Pas de photo"
    aperçu_voiture.short_description = "AUTO"

    def statut_service(self, obj):
        color = "#28a745" if obj.est_en_ligne else "#6c757d"
        label = "EN LIGNE" if obj.est_en_ligne else "HORS LIGNE"
        return format_html('<span style="background:{}; color:white; padding:4px 10px; border-radius:15px; font-weight:bold; font-size:10px;">{}</span>', color, label)
    statut_service.short_description = "SERVICE"

    def statut_abonnement(self, obj):
        if obj.est_actif:
            return format_html('<b style="color:#28a745;">✅ ACTIF</b>')
        return format_html('<b style="color:#dc3545;">❌ INACTIF</b>')
    statut_abonnement.short_description = "ABONNEMENT"

    def temps_restant(self, obj):
        if obj.date_expiration:
            jours = (obj.date_expiration - timezone.now()).days
            if jours > 0:
                return f"{jours} j"
            return format_html('<span style="color:red; font-weight:bold;">Expiré</span>')
        return "-"
    temps_restant.short_description = "RESTE"

    # --- 3. FICHE DE MODIFICATION (Simulation GPS incluse) ---
    fieldsets = (
        ("Identité & Photos", {
            'fields': ('nom_complet', 'telephone', 'plaque_immatriculation', 'photo_permis', 'photo_voiture')
        }),
        ("Simulation GPS", {
            'fields': ('latitude', 'longitude'),
            'description': "Modifiez ici pour tester votre carte Flutter (ecran_carte.dart)"
        }),
        ("Contrôle", {
            'fields': ('est_actif', 'est_en_ligne', 'date_expiration')
        }),
    )