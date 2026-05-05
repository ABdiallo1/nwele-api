from django.contrib import admin
from .models import Chauffeur
from django.utils.html import format_html

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # Ajout des colonnes 'aperçu_permis' et 'aperçu_voiture'
    list_display = (
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'est_actif', 
        'est_en_ligne', 
        'aperçu_permis', 
        'aperçu_voiture',
        'derniere_maj'
    )
    
    list_filter = ('est_actif', 'est_en_ligne')
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')
    list_editable = ('est_actif',)
    
    # Fonction pour afficher la miniature du permis
    def aperçu_permis(self, obj):
        if obj.photo_permis:
            return format_html('<img src="{}" style="width: 50px; height:50px; border-radius:5px;" />', obj.photo_permis.url)
        return "Pas de photo"
    aperçu_permis.short_description = 'Permis'

    # Fonction pour afficher la miniature du véhicule
    def aperçu_voiture(self, obj):
        if obj.photo_voiture:
            return format_html('<img src="{}" style="width: 50px; height:50px; border-radius:5px;" />', obj.photo_voiture.url)
        return "Pas de photo"
    aperçu_voiture.short_description = 'Véhicule'