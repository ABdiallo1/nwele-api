from django.contrib import admin
from django.utils.html import format_html
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # Correspond exactement aux champs de ton modèle
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
    
    fieldsets = (
        ('Identité', {'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')}),
        ('Documents', {'fields': ('photo_permis', 'photo_voiture')}),
        ('Statut Abonnement', {'fields': ('est_actif', 'date_expiration')}),
        ('Géolocalisation & Service', {'fields': ('est_en_ligne', 'latitude', 'longitude')}),
    )

    def apercu_permis(self, obj):
        # Sécurité : Vérifie si le fichier existe avant d'appeler .url
        if obj.photo_permis and hasattr(obj.photo_permis, 'url'):
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 5px; object-fit: cover;" />', obj.photo_permis.url)
        return "Pas de photo"
    apercu_permis.short_description = 'Permis'

    def apercu_voiture(self, obj):
        if obj.photo_voiture and hasattr(obj.photo_voiture, 'url'):
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 5px; object-fit: cover;" />', obj.photo_voiture.url)
        return "Pas de photo"
    apercu_voiture.short_description = 'Voiture'

    def statut_abonnement(self, obj):
        if obj.est_actif:
            return format_html('<b style="color: white; background: green; padding: 2px 8px; border-radius: 5px;">✔ ACTIF</b>')
        return format_html('<b style="color: white; background: #d33; padding: 2px 8px; border-radius: 5px;">✘ EXPIRÉ</b>')
    statut_abonnement.short_description = 'Abonnement'

    def jours_restants_display(self, obj):
        # Utilise la property @property jours_restants de ton modèle
        jours = obj.jours_restants
        couleur = "#28a745" if jours > 5 else "#dc3545"
        return format_html('<span style="color: {}; font-weight: bold;">{} jours</span>', couleur, jours)
    jours_restants_display.short_description = 'Reste'

    def statut_service(self, obj):
        if obj.est_en_ligne:
            return format_html('<span style="background: #28a745; color: white; padding: 3px 12px; border-radius: 12px; font-size: 10px;">EN LIGNE</span>')
        return format_html('<span style="background: #6c757d; color: white; padding: 3px 12px; border-radius: 12px; font-size: 10px;">HORS LIGNE</span>')
    statut_service.short_description = 'Service'