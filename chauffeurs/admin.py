from django.contrib import admin
from django.utils.html import format_html
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = (
        'apercu_permis', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', # <--- Ajouté ici
        'statut_abonnement', 
        'jours_restants_display',
        'statut_service'
    )
    
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')
    list_filter = ('est_actif', 'est_en_ligne')

    def statut_abonnement(self, obj):
        couleur = "green" if obj.est_actif else "red"
        return format_html('<b style="color: {};">{}</b>', couleur, "ACTIF" if obj.est_actif else "INACTIF")
    statut_abonnement.short_description = 'Abonnement'

    def apercu_permis(self, obj):
        if obj.photo_permis:
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 4px;"/>', obj.photo_permis.url)
        return "N/A"
    
    def jours_restants_display(self, obj):
        return f"{obj.jours_restants} j"