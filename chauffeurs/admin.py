from django.contrib import admin
from .models import Chauffeur

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    # On remplace 'nom' par 'nom_complet' dans la liste d'affichage
    list_display = ('id', 'nom_complet', 'telephone', 'est_actif', 'date_expiration')
    list_filter = ('est_actif', 'est_en_ligne')
    search_fields = ('nom_complet', 'telephone')
    ordering = ('-id',)