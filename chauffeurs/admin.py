from django.contrib import admin
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # Ajout de 'plaque_immatriculation' et 'est_en_ligne' dans la liste
    list_display = ('id', 'nom_complet', 'telephone', 'plaque_immatriculation', 'est_actif', 'est_en_ligne', 'date_expiration')
    
    # Ajout de filtres pour trier rapidement sur le côté
    list_filter = ('est_actif', 'est_en_ligne')
    
    # Champs de recherche
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')
    
    # Organisation de la fiche détaillée (quand tu cliques sur un chauffeur)
    fieldsets = (
        ("Infos Personnelles", {'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')}),
        ("Documents", {'fields': ('photo_permis', 'photo_voiture')}),
        ("Statuts & Abonnement", {'fields': ('est_actif', 'est_en_ligne', 'date_expiration')}),
        ("Localisation", {'fields': ('latitude', 'longitude')}),
    )