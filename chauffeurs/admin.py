from django.contrib import admin
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # On utilise uniquement des champs réels de la base pour éviter les erreurs de rendu
    list_display = (
        'aperçu_permis', 
        'aperçu_voiture', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'est_en_ligne', 
        'est_actif'
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
    def aperçu_permis(self, obj):
        if obj.photo_permis:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', obj.photo_permis.url)
        return "N/A"
    aperçu_permis.short_description = "PERMIS"

    def aperçu_voiture(self, obj):
        if obj.photo_voiture:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', obj.photo_voiture.url)
        return "N/A"
    aperçu_voiture.short_description = "AUTO"