from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = ('aperçu_permis', 'aperçu_voiture', 'nom_complet', 'telephone', 'statut_service', 'statut_abonnement', 'reste')
    list_editable = ('nom_complet',)
    search_fields = ('telephone', 'nom_complet')

    def aperçu_permis(self, obj):
        if obj.photo_permis:
            return mark_safe(f'<img src="{obj.photo_permis.url}" width="35" height="35" style="object-fit:cover; border-radius:4px;" />')
        return "📄"
    
    def aperçu_voiture(self, obj):
        if obj.photo_voiture:
            return mark_safe(f'<img src="{obj.photo_voiture.url}" width="35" height="35" style="object-fit:cover; border-radius:4px;" />')
        return "🚗"

    def statut_service(self, obj):
        color = "#28a745" if obj.est_en_ligne else "#dc3545"
        text = "EN LIGNE" if obj.est_en_ligne else "HORS LIGNE"
        return mark_safe(f'<span style="background:{color}; color:white; padding:3px 8px; border-radius:10px; font-size:10px;">{text}</span>')

    def statut_abonnement(self, obj):
        icon = "✅" if obj.est_actif else "❌"
        return mark_safe(f'<span>{icon}</span>')

    def reste(self, obj):
        if obj.date_expiration:
            delta = obj.date_expiration - timezone.now()
            if delta.days > 0: return f"{delta.days}j"
            return mark_safe('<span style="color:red;">EXP</span>')
        return "-"