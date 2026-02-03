from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = (
        'aperçu_permis', 
        'aperçu_voiture', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'statut_service', 
        'statut_abonnement', 
        'reste'
    )
    
    list_editable = ('nom_complet', 'telephone')
    
    # --- LA SOLUTION POUR LA LARGEUR DES CHAMPS ---
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'style': 'width: 120px; padding: 4px;'})},
    }

    # --- RENDU DES IMAGES ---
    def aperçu_permis(self, obj):
        try:
            if obj.photo_permis:
                return mark_safe(f'<img src="{obj.photo_permis.url}" width="35" height="35" style="object-fit:cover; border-radius:4px;" />')
        except: pass
        return "📄"
    aperçu_permis.short_description = "PERMIS"

    def aperçu_voiture(self, obj):
        try:
            if obj.photo_voiture:
                return mark_safe(f'<img src="{obj.photo_voiture.url}" width="35" height="35" style="object-fit:cover; border-radius:4px;" />')
        except: pass
        return "🚗"
    aperçu_voiture.short_description = "AUTO"

    # --- STATUTS ET RESTE (VERSIONS COURTES) ---
    def statut_service(self, obj):
        color = "#28a745" if obj.est_en_ligne else "#6c757d"
        text = "OUI" if obj.est_en_ligne else "NON"
        return mark_safe(f'<span style="background:{color}; color:white; padding:2px 8px; border-radius:10px; font-size:10px;">{text}</span>')
    statut_service.short_description = "SERVICE"

    def statut_abonnement(self, obj):
        icon = "✅" if obj.est_actif else "❌"
        return mark_safe(f'<span style="font-size:14px;">{icon}</span>')
    statut_abonnement.short_description = "ABON"

    def reste(self, obj):
        if obj.date_expiration:
            jours = (obj.date_expiration - timezone.now()).days
            return f"{jours}j" if jours > 0 else "EXP"
        return "-"
    reste.short_description = "RESTE"