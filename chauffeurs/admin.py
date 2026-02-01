from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # --- Configuration de la liste principale ---
    list_display = (
        'apercu_photo', 
        'apercu_voiture', 
        'nom', 
        'telephone', 
        'plaque_immatriculation',
        'statut_travail',   # Badge En ligne/Hors ligne
        'statut_paiement',  # Badge Actif/Expiré
        'jours_restants_display'
    )
    
    # Cliquer sur le nom pour ouvrir la fiche
    list_display_links = ('nom',)
    
    # Filtres rapides sur le côté droit
    list_filter = ('est_en_ligne', 'est_actif')
    
    # Barre de recherche
    search_fields = ('nom', 'telephone', 'plaque_immatriculation')

    # --- 1. Statut de Travail (Vert/Gris) ---
    def statut_travail(self, obj):
        if obj.est_en_ligne:
            return mark_safe('<span style="color:white; background:green; padding:3px 10px; border-radius:10px; font-weight:bold; font-size:10px;">EN LIGNE</span>')
        return mark_safe('<span style="color:white; background:gray; padding:3px 10px; border-radius:10px; font-size:10px;">HORS LIGNE</span>')
    statut_travail.short_description = "Service"

    # --- 2. Statut Paiement (Actif/Expiré) ---
    def statut_paiement(self, obj):
        if obj.est_actif:
            return mark_safe('<span style="color:green; font-weight:bold;">✅ ACTIF</span>')
        return mark_safe('<span style="color:red; font-weight:bold;">❌ EXPIRÉ</span>')
    statut_paiement.short_description = "Abonnement"

    # --- 3. Aperçu Photos (Permis et Voiture) ---
    def apercu_photo(self, obj):
        if obj.photo_permis:
            return mark_safe(f'<a href="{obj.photo_permis.url}" target="_blank">'
                             f'<img src="{obj.photo_permis.url}" style="width:45px; height:45px; border-radius:5px; object-fit:cover; border:1px solid #ddd;" /></a>')
        return "N/A"
    apercu_photo.short_description = "Permis"

    def apercu_voiture(self, obj):
        if obj.photo_voiture:
            return mark_safe(f'<a href="{obj.photo_voiture.url}" target="_blank">'
                             f'<img src="{obj.photo_voiture.url}" style="width:45px; height:45px; border-radius:5px; object-fit:cover; border:1px solid #ddd;" /></a>')
        return "N/A"
    apercu_voiture.short_description = "Auto"

    # --- 4. Décompte des jours restants ---
    def jours_restants_display(self, obj):
        nb = obj.jours_restants() # Utilise la méthode de ton modèle
        if nb > 5:
            return f"{nb} j"
        elif nb > 0:
            return mark_safe(f'<span style="color:orange; font-weight:bold;">{nb} j</span>')
        return mark_safe('<span style="color:red; font-weight:bold;">Expiré</span>')
    jours_restants_display.short_description = "Reste"