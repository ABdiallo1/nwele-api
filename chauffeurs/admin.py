from django.contrib import admin
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # Liste des colonnes affichées dans l'admin
    list_display = ('nom_complet', 'telephone', 'plaque_immatriculation', 'est_actif', 'est_en_ligne', 'derniere_maj')
    
    # Filtres sur le côté droit
    list_filter = ('est_actif', 'est_en_ligne')
    
    # Barre de recherche
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')
    
    # Permet de modifier le statut "actif" directement depuis la liste
    list_editable = ('est_actif',)