from django.contrib import admin
from django.utils.html import format_html
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # On définit ici EXACTEMENT les colonnes que l'on veut voir
    list_display = (
        'apercu_permis', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation',  # <--- On l'ajoute explicitement ici
        'statut_abonnement', 
        'jours_restants_display',
        'statut_service'
    )
    
    list_filter = ('est_actif', 'est_en_ligne')
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')

    # --- Fonctions d'affichage personnalisées ---

    def apercu_permis(self, obj):
        if obj.photo_permis:
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 4px;" />', obj.photo_permis.url)
        return "Non fourni"
    apercu_permis.short_description = 'Permis'

    def statut_abonnement(self, obj):
        if obj.est_actif:
            return format_html('<b style="color: green;">✔ ACTIF</b>')
        return format_html('<b style="color: red;">✘ EXPIRÉ</b>')
    statut_abonnement.short_description = 'Abonnement'

    def jours_restants_display(self, obj):
        jours = obj.jours_restants
        couleur = "green" if jours > 0 else "red"
        return format_html('<span style="color: {}; font-weight: bold;">{} j</span>', couleur, jours)
    jours_restants_display.short_description = 'Reste'

    def statut_service(self, obj):
        if obj.est_en_ligne:
            return format_html('<span style="background: green; color: white; padding: 3px 10px; border-radius: 10px;">EN LIGNE</span>')
        return format_html('<span style="background: red; color: white; padding: 3px 10px; border-radius: 10px;">HORS LIGNE</span>')
    statut_service.short_description = 'Service'