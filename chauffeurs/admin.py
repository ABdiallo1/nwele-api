from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # 1. Configuration de la liste principale (Look C_36)
    list_display = (
        'aperçu_permis', 
        'aperçu_voiture', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'statut_service', 
        'statut_abonnement', 
        'reste'
    )
    
    list_editable = ('nom_complet', 'telephone')
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')
    list_filter = ('est_actif', 'est_en_ligne')

    # --- 2. RENDU DES IMAGES (SÉCURISÉ CONTRE LES ERREURS RENDER) ---
    def aperçu_permis(self, obj):
        try:
            if obj.photo_permis and hasattr(obj.photo_permis, 'url'):
                return mark_safe(f'<img src="{obj.photo_permis.url}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />')
        except:
            pass
        return "📄"
    aperçu_permis.short_description = "PERMIS"

    def aperçu_voiture(self, obj):
        try:
            if obj.photo_voiture and hasattr(obj.photo_voiture, 'url'):
                return mark_safe(f'<img src="{obj.photo_voiture.url}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />')
        except:
            pass
        return "🚗"
    aperçu_voiture.short_description = "AUTO"

    # --- 3. BADGES DE STATUT (LOOK C_36) ---
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
            if days > 0:
                return f"{days} j"
            return mark_safe('<span style="color:red;">Expiré</span>')
        return "-"
    reste.short_description = "RESTE"

    # --- 4. FICHE DE MODIFICATION (Pour ecran_carte.dart) ---
    fieldsets = (
        ("Chauffeur", {
            'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')
        }),
        ("Photos", {
            'fields': ('photo_permis', 'photo_voiture')
        }),
        ("Position Simulation (Flutter)", {
            'fields': ('latitude', 'longitude'),
            'description': "Modifiez ici pour voir le chauffeur bouger sur ecran_carte.dart"
        }),
        ("Statut", {
            'fields': ('est_actif', 'est_en_ligne', 'date_expiration')
        }),
    )