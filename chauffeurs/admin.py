from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # On définit les colonnes exactement comme C_36
    list_display = (
        'aperçu_permis', 
        'aperçu_voiture', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'service', 
        'abonnement', 
        'reste'
    )
    
    # On enlève latitude/longitude de la liste pour ne pas encombrer
    list_editable = ('nom_complet', 'telephone')
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')

    # --- FONCTIONS DE RENDU SIMPLIFIÉES (Anti-Crash) ---

    def aperçu_permis(self, obj):
        if obj.photo_permis and hasattr(obj.photo_permis, 'url'):
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover;border-radius:4px;"/>', obj.photo_permis.url)
        return "N/A"
    aperçu_permis.short_description = "PERMIS"

    def aperçu_voiture(self, obj):
        if obj.photo_voiture and hasattr(obj.photo_voiture, 'url'):
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover;border-radius:4px;"/>', obj.photo_voiture.url)
        return "N/A"
    aperçu_voiture.short_description = "AUTO"

    def service(self, obj):
        color = "#28a745" if obj.est_en_ligne else "#6c757d"
        txt = "EN LIGNE" if obj.est_en_ligne else "HORS LIGNE"
        return format_html('<span style="background:{};color:white;padding:3px 8px;border-radius:10px;font-size:10px;font-weight:bold;">{}</span>', color, txt)

    def abonnement(self, obj):
        symbol = "✅ ACTIF" if obj.est_actif else "❌ INACTIF"
        color = "#28a745" if obj.est_actif else "#dc3545"
        return format_html('<span style="color:{};font-weight:bold;">{}</span>', color, symbol)

    def reste(self, obj):
        if obj.date_expiration:
            diff = obj.date_expiration - timezone.now()
            days = diff.days
            if days > 0: return f"{days} j"
            return format_html('<span style="color:red;font-weight:bold;">Expiré</span>')
        return "-"

    # La simulation GPS reste disponible quand tu cliques sur le chauffeur
    fieldsets = (
        ("Identité", {'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')}),
        ("Photos", {'fields': ('photo_permis', 'photo_voiture')}),
        ("Simulation GPS", {'fields': ('latitude', 'longitude')}),
        ("Statut", {'fields': ('est_actif', 'est_en_ligne', 'date_expiration')}),
    )