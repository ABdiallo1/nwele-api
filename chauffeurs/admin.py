from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = (
        'apercu_photo', 'apercu_voiture', 'nom', 'telephone', 
        'plaque_immatriculation', 'statut_travail', 
        'statut_paiement', 'jours_restants_display'
    )
    list_display_links = ('nom',)
    list_filter = ('est_en_ligne', 'est_actif')
    search_fields = ('nom', 'telephone', 'plaque_immatriculation')

    def statut_travail(self, obj):
        color = "green" if obj.est_en_ligne else "gray"
        text = "EN LIGNE" if obj.est_en_ligne else "HORS LIGNE"
        return mark_safe(f'<span style="color:white; background:{color}; padding:3px 10px; border-radius:10px; font-weight:bold; font-size:10px;">{text}</span>')

    def statut_paiement(self, obj):
        if obj.est_actif:
            return mark_safe('<span style="color:green; font-weight:bold;">✅ ACTIF</span>')
        return mark_safe('<span style="color:red; font-weight:bold;">❌ EXPIRÉ</span>')

    def apercu_photo(self, obj):
        if obj.photo_permis:
            return mark_safe(f'<img src="{obj.photo_permis.url}" style="width:40px; height:40px; border-radius:5px; object-fit:cover;" />')
        return "N/A"

    def apercu_voiture(self, obj):
        if obj.photo_voiture:
            return mark_safe(f'<img src="{obj.photo_voiture.url}" style="width:40px; height:40px; border-radius:5px; object-fit:cover;" />')
        return "N/A"

    def jours_restants_display(self, obj):
        nb = obj.jours_restants()
        color = "red" if nb <= 0 else "orange" if nb <= 5 else "black"
        return mark_safe(f'<span style="color:{color}; font-weight:bold;">{nb if nb > 0 else "Expiré"}</span>')