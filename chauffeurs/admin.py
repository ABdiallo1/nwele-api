from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # On garde l'ordre exact de C_36
    list_display = ('aperçu_permis', 'aperçu_voiture', 'nom_complet', 'telephone', 'plaque_immatriculation', 'statut_service', 'statut_abonnement', 'reste')
    
    # --- MÉTHODES DE RENDU HYPER-SÉCURISÉES ---

    def aperçu_permis(self, obj):
        if obj.photo_permis:
            # On utilise f-string pour éviter les erreurs d'arguments de format_html
            url = obj.photo_permis.url
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', url)
        return "N/A"
    aperçu_permis.short_description = "PERMIS"

    def aperçu_voiture(self, obj):
        if obj.photo_voiture:
            url = obj.photo_voiture.url
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', url)
        return "N/A"
    aperçu_voiture.short_description = "AUTO"

    def statut_service(self, obj):
        color = "#28a745" if obj.est_en_ligne else "#6c757d"
        txt = "EN LIGNE" if obj.est_en_ligne else "HORS LIGNE"
        return format_html('<span style="background:{}; color:white; padding:4px 8px; border-radius:12px; font-weight:bold; font-size:10px;">{}</span>', color, txt)
    statut_service.short_description = "SERVICE"

    def statut_abonnement(self, obj):
        if obj.est_actif:
            return format_html('<b style="color:#28a745;">✅ ACTIF</b>')
        return format_html('<b style="color:#dc3545;">❌ INACTIF</b>')
    statut_abonnement.short_description = "ABONNEMENT"

    def reste(self, obj):
        if obj.date_expiration:
            jours = (obj.date_expiration - timezone.now()).days
            return f"{jours} j" if jours > 0 else "Expiré"
        return "-"
    reste.short_description = "RESTE"

    # Simulation GPS toujours accessible dans la fiche pour ecran_carte.dart
    fieldsets = (
        ("Identité", {'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')}),
        ("Photos", {'fields': ('photo_permis', 'photo_voiture')}),
        ("Simulation GPS", {'fields': ('latitude', 'longitude')}),
        ("État", {'fields': ('est_actif', 'est_en_ligne', 'date_expiration')}),
    )