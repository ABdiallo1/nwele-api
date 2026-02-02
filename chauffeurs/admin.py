from django.contrib import admin
from django.utils.html import format_html
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # 1. On ajoute les colonnes des photos et de la plaque dans list_display
    list_display = (
        'id', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'aperçu_voiture',  # Affiche la miniature de la voiture
        'est_actif', 
        'est_en_ligne', 
        'date_expiration'
    )
    
    list_editable = ('est_actif', 'est_en_ligne') 
    list_filter = ('est_actif', 'est_en_ligne')
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')

    # 2. On organise la fiche de modification (quand on clique sur le chauffeur)
    fieldsets = (
        ("Identité & Véhicule", {
            'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')
        }),
        ("Documents Photos", {
            'fields': ('photo_permis', 'photo_voiture'),
        }),
        ("Statut", {
            'fields': ('est_actif', 'est_en_ligne', 'date_expiration')
        }),
    )

    # 3. Fonction pour afficher la miniature de la voiture dans le tableau
    def aperçu_voiture(self, obj):
        if obj.photo_voiture:
            return format_html('<img src="{}" style="width: 50px; height: auto; border-radius: 5px;" />', obj.photo_voiture.url)
        return "Pas de photo"
    
    aperçu_voiture.short_description = "Véhicule"