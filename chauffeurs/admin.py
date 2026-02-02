from django.contrib import admin
from django.utils.html import format_html
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # --- 1. TON TABLEAU DE BORD (Vue Liste comme C_36) ---
    list_display = (
        'id', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'aperçu_voiture',  # Miniature de la voiture
        'latitude',        # Visible pour tes simulations
        'longitude',       # Visible pour tes simulations
        'est_actif', 
        'est_en_ligne', 
        'date_expiration'
    )
    
    # Rendre les champs modifiables directement sans ouvrir la fiche
    list_editable = ('est_actif', 'est_en_ligne', 'latitude', 'longitude') 

    list_filter = ('est_actif', 'est_en_ligne')
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')

    # --- 2. TA FICHE DÉTAILLÉE (Comme C_77) ---
    fieldsets = (
        ("Identité & Véhicule", {
            'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')
        }),
        ("Localisation (Simulations)", {
            'fields': ('latitude', 'longitude'),
            'description': "Modifiez ces valeurs pour simuler le déplacement du chauffeur sur la carte."
        }),
        ("Documents Photos", {
            'fields': ('photo_permis', 'photo_voiture'),
        }),
        ("Statut & Abonnement", {
            'fields': ('est_actif', 'est_en_ligne', 'date_expiration')
        }),
    )

    # --- 3. FONCTION POUR L'IMAGE ---
    def aperçu_voiture(self, obj):
        if obj.photo_voiture:
            return format_html('<img src="{}" style="width: 50px; height: auto; border-radius: 5px;" />', obj.photo_voiture.url)
        return "Pas de photo"
    
    aperçu_voiture.short_description = "Véhicule"