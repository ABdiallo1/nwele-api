from django.contrib import admin
from django.utils.html import format_html
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = ('apercu_permis', 'apercu_vehicule', 'nom_complet', 'telephone', 'est_actif')
    
    def apercu_permis(self, obj):
        if obj.photo_permis:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.photo_permis.url)
        return "Pas d'image"

    def apercu_vehicule(self, obj):
        if obj.photo_vehicule:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.photo_vehicule.url)
        return "Pas d'image"

    apercu_permis.short_description = "Permis"
    apercu_vehicule.short_description = "Véhicule"