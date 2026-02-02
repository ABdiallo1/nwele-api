from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # 1. AFFICHAGE : Exactement comme C_36 (Pas de GPS ici)
    list_display = (
        'aperçu_permis', 
        'aperçu_voiture', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'service', 
        'abonnement', 
        'reste'
    )
    
    # On retire latitude/longitude de list_editable puisqu'elles ne sont plus affichées
    list_editable = ('nom_complet', 'telephone') 
    
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')
    list_filter = ('est_actif', 'est_en_ligne')

    # --- 2. SIMULATION : Visible uniquement dans la fiche (Comme C_77) ---
    fieldsets = (
        ("Identité & Photos", {
            'fields': ('nom_complet', 'telephone', 'plaque_immatriculation', 'photo_permis', 'photo_voiture')
        }),
        ("Simulation GPS", {
            'fields': ('latitude', 'longitude'),
            'description': "Modifiez ces coordonnées pour simuler la position sur la carte."
        }),
        ("Statut & Abonnement", {
            'fields': ('est_actif', 'est_en_ligne', 'date_expiration')
        }),
    )

    # --- MÉTHODES DE RENDU POUR LE LOOK C_36 ---
    def aperçu_permis(self, obj):
        if obj.photo_permis:
            return format_html('<img src="{}" style="width:45px; height:45px; object-fit:cover; border-radius:4px;" />', obj.photo_permis.url)
        return "N/A"
    aperçu_permis.short_description = "PERMIS"

    def aperçu_voiture(self, obj):
        if obj.photo_voiture:
            return format_html('<img src="{}" style="width:45px; height:45px; object-fit:cover; border-radius:4px;" />', obj.photo_voiture.url)
        return "N/A"
    aperçu_voiture.short_description = "AUTO"

    def service(self, obj):
        color = "#28a745" if obj.est_en_ligne else "#6c757d"
        text = "EN LIGNE" if obj.est_en_ligne else "HORS LIGNE"
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:12px; font-weight:bold; font-size:11px;">{}</span>', color, text)

    def abonnement(self, obj):
        if obj.est_actif:
            return format_html('<span style="color:#28a745; font-weight:bold;">✅ ACTIF</span>')
        return format_html('<span style="color:#dc3545; font-weight:bold;">❌ INACTIF</span>')

    def reste(self, obj):
        if obj.date_expiration:
            diff = obj.date_expiration - timezone.now()
            days = diff.days
            if days > 0:
                return f"{days} j"
            return format_html('<span style="color:#dc3545; font-weight:bold;">Expiré</span>')
        return "-"