from django.contrib import admin
from django.utils.html import format_html
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = (
        'apercu_permis', 
        'apercu_voiture', 
        'nom_complet', 
        'telephone', 
        'statut_abonnement', 
        'jours_restants_display',
        'statut_service'
    )
    
    list_filter = ('est_actif', 'est_en_ligne', 'date_expiration')
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')

    def apercu_permis(self, obj):
        if obj.photo_permis and hasattr(obj.photo_permis, 'url'):
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 4px; object-fit: cover;" />', obj.photo_permis.url)
        return "N/A"
    apercu_permis.short_description = 'Permis'

    def apercu_voiture(self, obj):
        if obj.photo_voiture and hasattr(obj.photo_voiture, 'url'):
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 4px; object-fit: cover;" />', obj.photo_voiture.url)
        return "N/A"
    apercu_voiture.short_description = 'Voiture'

    def statut_abonnement(self, obj):
        couleur = "green" if obj.est_actif else "red"
        texte = "ACTIF" if obj.est_actif else "INACTIF"
        return format_html('<b style="color: {};">{}</b>', couleur, texte)
    statut_abonnement.short_description = 'Abonnement'

    def jours_restants_display(self, obj):
        return f"{obj.jours_restants} jours"
    jours_restants_display.short_description = 'Repos'

    def statut_service(self, obj):
        icon = "✅" if obj.est_en_ligne else "❌"
        return format_html('<span>{}</span>', icon)
    statut_service.short_description = 'En Service'