from django.contrib import admin
from django.utils.html import format_html
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # Configuration des colonnes affichées dans la liste
    list_display = (
        'apercu_permis', 
        'nom_complet', 
        'telephone', 
        'plaque_immatriculation', 
        'statut_abonnement', 
        'jours_restants_display',
        'statut_service'
    )
    
    # Barre de recherche et filtres latéraux
    search_fields = ('nom_complet', 'telephone', 'plaque_immatriculation')
    list_filter = ('est_actif', 'est_en_ligne')
    
    # Permet de modifier le statut directement depuis la liste (utile pour le debug)
    list_editable = ('plaque_immatriculation',)

    def statut_abonnement(self, obj):
        """ Affiche 'ACTIF' en vert ou 'INACTIF' en rouge """
        couleur = "green" if obj.est_actif else "red"
        texte = "ACTIF" if obj.est_actif else "INACTIF"
        return format_html('<b style="color: {};">{}</b>', couleur, texte)
    statut_abonnement.short_description = 'ABONNEMENT'

    def apercu_permis(self, obj):
        """ Affiche une miniature de la photo du permis avec gestion d'erreur """
        if obj.photo_permis:
            try:
                # On vérifie que l'URL est accessible pour éviter l'erreur 500
                url = obj.photo_permis.url
                return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 5px; object-fit: cover; border: 1px solid #ddd;"/>', url)
            except (ValueError, AttributeError):
                return format_html('<span style="color: orange;">Fichier manquant</span>')
        return format_html('<span style="color: #999;">Aucun</span>')
    apercu_permis.short_description = 'PERMIS'
    
    def jours_restants_display(self, obj):
        """ Affiche le décompte des jours """
        jours = obj.jours_restants
        couleur = "orange" if jours < 3 else "black"
        return format_html('<span style="color: {};">{} j</span>', couleur, jours)
    jours_restants_display.short_description = 'REPOS'

    def statut_service(self, obj):
        """ Affiche une icône visuelle pour le service """
        icon = "✅" if obj.est_en_ligne else "❌"
        return format_html('<span style="font-size: 1.2em; display: block; text-align: center;">{}</span>', icon)
    statut_service.short_description = 'SERVICE'

    # Organisation des champs dans le formulaire de modification
    fieldsets = (
        ('Informations Personnelles', {
            'fields': ('nom_complet', 'telephone', 'plaque_immatriculation')
        }),
        ('Documents', {
            'fields': ('photo_permis', 'photo_voiture')
        }),
        ('Statut du Compte', {
            'fields': ('est_actif', 'date_expiration', 'est_en_ligne')
        }),
        ('Géolocalisation', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',), # Cache cette section par défaut
        }),
    )