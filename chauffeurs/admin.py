from django.contrib import admin
from django.utils.html import format_html
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = ('apercu_permis', 'apercu_voiture', 'nom_complet', 'telephone', 'statut_abonnement', 'statut_service')
    list_filter = ('est_actif', 'est_en_ligne', 'date_expiration')
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')

    def apercu_permis(self, obj):
        # On vérifie si le fichier existe physiquement avant de demander l'URL
        if obj.photo_permis and hasattr(obj.photo_permis, 'url'):
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 5px;"/>', obj.photo_permis.url)
        return "Pas de photo"
    apercu_permis.short_description = 'Permis'

    def apercu_voiture(self, obj):
        if obj.photo_voiture and hasattr(obj.photo_voiture, 'url'):
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 5px;"/>', obj.photo_voiture.url)
        return "Pas de photo"
    apercu_voiture.short_description = 'Voiture'

    def statut_abonnement(self, obj):
        if obj.est_actif:
            return format_html('<b style="color: green;">✔ ACTIF</b>')
        return format_html('<b style="color: red;">✘ EXPIRÉ</b>')
    
    def statut_service(self, obj):
        couleur = "green" if obj.est_en_ligne else "grey"
        texte = "EN LIGNE" if obj.est_en_ligne else "HORS LIGNE"
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', couleur, texte)