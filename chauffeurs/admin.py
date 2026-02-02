from django.contrib import admin
from django.utils.html import format_html  # <--- CETTE LIGNE MANQUAIT (image_565b10.png)
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # Affichage identique au look C_36
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
    
    list_editable = ('nom_complet', 'telephone')
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')

    # --- RENDU SÉCURISÉ DES IMAGES (C_36) ---
    def aperçu_permis(self, obj):
        if obj.photo_permis and hasattr(obj.photo_permis, 'url'):
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', obj.photo_permis.url)
        return "N/A"
    aperçu_permis.short_description = "PERMIS"

    def aperçu_voiture(self, obj):
        if obj.photo_voiture and hasattr(obj.photo_voiture, 'url'):
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', obj.photo_voiture.url)
        return "N/A"
    aperçu_voiture.short_description = "AUTO"

    # --- BADGES DE STATUT (C_36) ---
    def statut_service(self, obj):
        color = "#28a745" if obj.est_en_ligne else "#6c757d"
        text = "EN LIGNE" if obj.est_en_ligne else "HORS LIGNE"
        return format_html('<span style="background:{}; color:white; padding:4px 10px; border-radius:15px; font-size:10px; font-weight:bold;">{}</span>', color, text)
    statut_service.short_description = "SERVICE"

    def statut_abonnement(self, obj):
        if obj.est_actif:
            return format_html('<b style="color:#28a745;">✅ ACTIF</b>')
        return format_html('<b style="color:#dc3545;">❌ INACTIF</b>')
    statut_abonnement.short_description = "ABONNEMENT"

    def temps_restant(self, obj):
        if obj.date_expiration:
            jours = (obj.date_expiration - timezone.now()).days
            return f"{jours} j" if jours > 0 else "Expiré"
        return "-"
    temps_restant.short_description = "RESTE"

    # --- FICHE DE MODIFICATION (Pour tes tests GPS) ---
    fieldsets = (
        ("Chauffeur", {'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')}),
        ("Photos", {'fields': ('photo_permis', 'photo_voiture')}),
        ("Simulation GPS (Flutter)", {'fields': ('latitude', 'longitude')}),
        ("État", {'fields': ('est_actif', 'est_en_ligne', 'date_expiration')}),
    )