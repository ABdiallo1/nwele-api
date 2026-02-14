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
    
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'style': 'width: 120px; padding: 4px;'})},
    }

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

    # --- AFFICHAGE DU SERVICE (EN LIGNE / HORS LIGNE) ---
    def statut_service(self, obj):
        # Utilise le champ est_en_ligne du modèle
        color = "#28a745" if obj.est_en_ligne else "#dc3545" # Vert si oui, Rouge si non
        text = "OUI" if obj.est_en_ligne else "NON"
        return mark_safe(f'<span style="background:{color}; color:white; padding:3px 10px; border-radius:10px; font-size:10px; font-weight:bold;">{text}</span>')
    statut_service.short_description = "SERVICE"

    def statut_abonnement(self, obj):
        icon = "✅" if obj.est_actif else "❌"
        return mark_safe(f'<span style="font-size:14px;">{icon}</span>')
    statut_abonnement.short_description = "ABON"

    def reste(self, obj):
        if obj.date_expiration:
            # Correction : utilise timezone.now() pour comparer des dates avec fuseau horaire
            delta = obj.date_expiration - timezone.now()
            jours = delta.days
            if jours > 0:
                return f"{jours}j"
            return mark_safe('<span style="color:red; font-weight:bold;">EXP</span>')
        return "-"
    reste.short_description = "RESTE"