from django.contrib import admin
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # Configuration de la vue en liste (ton tableau de bord)
    list_display = (
        'id', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'est_actif',     # Icône Vert/Rouge pour l'abonnement
        'est_en_ligne',  # Icône Vert/Rouge pour la présence
        'date_expiration'
    )
    
    # Permet de modifier le statut "Actif" directement depuis la liste sans ouvrir la fiche
    list_editable = ('est_actif',) 

    # Ajoute des filtres sur la droite pour voir par exemple uniquement ceux "En ligne"
    list_filter = ('est_actif', 'est_en_ligne')
    
    # Barre de recherche pour trouver un chauffeur par nom, tel ou plaque
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')
    
    # Organisation de la fiche de modification (quand tu cliques sur l'ID)
    fieldsets = (
        ("Identité du Chauffeur", {
            'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')
        }),
        ("Documents & Photos", {
            'fields': ('photo_permis', 'photo_voiture'),
            'description': "Cliquez sur les liens pour voir les photos envoyées."
        }),
        ("Gestion & Surveillance", {
            'fields': ('est_actif', 'est_en_ligne', 'date_expiration')
        }),
        ("Géolocalisation", {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',) # Cache cette section par défaut
        }),
    )