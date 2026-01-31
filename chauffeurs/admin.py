from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # On met TOUT dans la même liste
    list_display = (
        'apercu_photo', 
        'apercu_voiture', 
        'nom', 
        'telephone', 
        'plaque_immatriculation',
        'statut_travail',   # Statut de connexion (En ligne/Hors ligne)
        'statut_paiement',  # Statut de l'abonnement (Actif/Expiré)
        'jours_restants_display'
    )
    
    list_display_links = ('nom',)
    # Filtres pour trier rapidement sur le côté
    list_filter = ('est_en_ligne', 'est_actif')
    search_fields = ('nom', 'telephone', 'plaque_immatriculation')

    # --- 1. Statut de Travail (Vert/Gris) ---
    def statut_travail(self, obj):
        if obj.est_en_ligne:
            return mark_safe('<span style="color:white; background:green; padding:3px 10px; border-radius:10px; font-weight:bold;">EN LIGNE</span>')
        return mark_safe('<span style="color:white; background:gray; padding:3px 10px; border-radius:10px;">HORS LIGNE</span>')
    statut_travail.short_description = "Service"

    # --- 2. Statut Paiement (Actif/Expiré) ---
    def statut_paiement(self, obj):
        if obj.est_actif:
            return mark_safe('<span style="color:green; font-weight:bold;">✅ ACTIF</span>')
        return mark_safe('<span style="color:red; font-weight:bold;">❌ EXPIRÉ</span>')
    statut_paiement.short_description = "Abonnement"

    # --- 3. Photos ---
    def apercu_photo(self, obj):
        if obj.photo_permis:
            return mark_safe(f'<a href="{obj.photo_permis.url}" target="_blank">'
                             f'<img src="{obj.photo_permis.url}" style="width:45px; height:45px; border-radius:5px; object-fit:cover;" /></a>')
        return "N/A"
    apercu_photo.short_description = "Permis"

    def apercu_voiture(self, obj):
        if obj.photo_voiture:
            return mark_safe(f'<a href="{obj.photo_voiture.url}" target="_blank">'
                             f'<img src="{obj.photo_voiture.url}" style="width:45px; height:45px; border-radius:5px; object-fit:cover;" /></a>')
        return "N/A"
    apercu_voiture.short_description = "Auto"

    # --- 4. Décompte des jours ---
    def jours_restants_display(self, obj):
        nb = obj.jours_restants()
        if nb > 5:
            return f"{nb} j"
        elif nb > 0:
            return mark_safe(f'<span style="color:orange; font-weight:bold;">{nb} j</span>')
        return mark_safe('<span style="color:red; font-weight:bold;">Expiré</span>')
    jours_restants_display.short_description = "Reste"