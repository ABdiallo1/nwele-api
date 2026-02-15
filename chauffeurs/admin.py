from django.contrib import admin
from django.utils.html import format_html
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = (
        'apercu_permis', 
        'apercu_voiture', 
        'nom_complet', 
        'telephone', 
        'statut_abonnement', 
        'jours_restants_display',
        'est_en_ligne'
    )
    
    # Filtres sur le côté droit
    list_filter = ('est_actif', 'est_en_ligne')
    
    # Barre de recherche
    search_fields = ('nom_complet', 'telephone')

    def apercu_permis(self, obj):
        if obj.photo_permis:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 5px;" />', obj.photo_permis.url)
        return "Pas de photo"
    apercu_permis.short_description = 'Permis'

    def apercu_voiture(self, obj):
        if obj.photo_voiture:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 5px;" />', obj.photo_voiture.url)
        return "Pas de photo"
    apercu_voiture.short_description = 'Voiture'

    def statut_abonnement(self, obj):
        if obj.est_actif:
            return format_html('<b style="color: green;">✔ ACTIF</b>')
        return format_html('<b style="color: red;">✘ INACTIF</b>')
    statut_abonnement.short_description = 'Abonnement'

    def jours_restants_display(self, obj):
        jours = obj.jours_restants
        color = "green" if jours > 5 else "red"
        return format_html('<span style="color: {};">{} jours</span>', color, jours)
    jours_restants_display.short_description = 'Reste'