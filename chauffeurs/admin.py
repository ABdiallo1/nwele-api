from django.contrib import admin
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # On utilise uniquement des champs réels de la base pour éviter les erreurs de rendu
    list_display = (
        'id', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'est_en_ligne', 
        'est_actif', 
        'date_expiration'
    )
    
    # Très important pour tes simulations GPS sans ouvrir la fiche
    list_editable = ('est_actif', 'est_en_ligne') 
    
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')
    list_filter = ('est_actif', 'est_en_ligne')

    # Organisation de la fiche (C_77) pour tes tests Flutter
    fieldsets = (
        ("Identité", {
            'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')
        }),
        ("Photos & Documents", {
            'fields': ('photo_permis', 'photo_voiture'),
        }),
        ("Simulation GPS (pour ecran_carte.dart)", {
            'fields': ('latitude', 'longitude'),
        }),
        ("Gestion", {
            'fields': ('est_actif', 'est_en_ligne', 'date_expiration')
        }),
    )