from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # 1. Configuration de la liste (Exactement comme C_36)
    list_display = (
        'get_permis', 
        'get_auto', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'get_service', 
        'get_abonnement', 
        'get_reste'
    )
    
    # Pas de colonnes GPS ici pour rester comme C_36
    list_editable = ('nom_complet', 'telephone')
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')

    # --- 2. MÉTHODES DE RENDU SÉCURISÉES ---

    def get_permis(self, obj):
        if obj.photo_permis:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', obj.photo_permis.url)
        return "N/A"
    get_permis.short_description = "PERMIS"

    def get_auto(self, obj):
        if obj.photo_voiture:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', obj.photo_voiture.url)
        return "N/A"
    get_auto.short_description = "AUTO"

    def get_service(self, obj):
        color = "#28a745" if obj.est_en_ligne else "#6c757d"
        label = "EN LIGNE" if obj.est_en_ligne else "HORS LIGNE"
        return format_html('<span style="background:{}; color:white; padding:3px 8px; border-radius:10px; font-weight:bold; font-size:10px;">{}</span>', color, label)
    get_service.short_description = "SERVICE"

    def get_abonnement(self, obj):
        if obj.est_actif:
            return format_html('<span style="color:#28a745; font-weight:bold;">✅ ACTIF</span>')
        return format_html('<span style="color:#dc3545; font-weight:bold;">❌ INACTIF</span>')
    get_abonnement.short_description = "ABONNEMENT"

    def get_reste(self, obj):
        if obj.date_expiration:
            diff = obj.date_expiration - timezone.now()
            days = diff.days
            if days > 0:
                return f"{days} j"
            return format_html('<span style="color:red; font-weight:bold;">Expiré</span>')
        return "-"
    get_reste.short_description = "RESTE"

    # --- 3. FICHE DE MODIFICATION (Simulation GPS ici comme C_77) ---
    fieldsets = (
        ("Identité", {'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')}),
        ("Photos", {'fields': ('photo_permis', 'photo_voiture')}),
        ("Simulation GPS", {'fields': ('latitude', 'longitude')}),
        ("Abonnement & Statut", {'fields': ('est_actif', 'est_en_ligne', 'date_expiration')}),
    )