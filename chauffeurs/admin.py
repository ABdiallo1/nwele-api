from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
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

    # --- ASTUCE POUR RÉDUIRE LA TAILLE DES CHAMPS ---
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        # On injecte du CSS directement pour aller plus vite
    
    def get_list_display_links(self, request, list_display):
        # On permet de cliquer sur la plaque pour ouvrir la fiche
        return ('plaque_immatriculation',)

    # --- RENDU DES IMAGES ---
    def aperçu_permis(self, obj):
        try:
            if obj.photo_permis:
                return mark_safe(f'<img src="{obj.photo_permis.url}" width="35" height="35" style="object-fit:cover; border-radius:4px;" />')
        except: pass
        return "📄"
    aperçu_permis.short_description = "PERMIS"

    def aperçu_voiture(self, obj):
        try:
            if obj.photo_voiture:
                return mark_safe(f'<img src="{obj.photo_voiture.url}" width="35" height="35" style="object-fit:cover; border-radius:4px;" />')
        except: pass
        return "🚗"
    aperçu_voiture.short_description = "AUTO"

    # --- STATUTS COMPACTS ---
    def statut_service(self, obj):
        color = "#28a745" if obj.est_en_ligne else "#6c757d"
        text = "OUI" if obj.est_en_ligne else "NON"
        return mark_safe(f'<span style="background:{color}; color:white; padding:2px 8px; border-radius:10px; font-size:10px;">{text}</span>')
    statut_service.short_description = "SERVICE"

    def statut_abonnement(self, obj):
        color = "#28a745" if obj.est_actif else "#dc3545"
        icon = "✅" if obj.est_actif else "❌"
        return mark_safe(f'<span style="color:{color}; font-weight:bold;">{icon}</span>')
    statut_abonnement.short_description = "ABON"

    def reste(self, obj):
        if obj.date_expiration:
            jours = (obj.date_expiration - timezone.now()).days
            return f"{jours}j" if jours > 0 else mark_safe('<span style="color:red;">EXP</span>')
        return "-"
    reste.short_description = "RESTE"

    fieldsets = (
        ("Chauffeur", {'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')}),
        ("Photos", {'fields': ('photo_permis', 'photo_voiture')}),
        ("Simulation GPS", {'fields': ('latitude', 'longitude')}),
        ("Statut", {'fields': ('est_actif', 'est_en_ligne', 'date_expiration')}),
    )