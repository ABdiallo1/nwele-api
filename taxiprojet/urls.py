from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from chauffeurs import views

urlpatterns = [
    # Interface d'administration
    path('admin/', admin.site.urls),
    
    # API pour l'application Flutter
    path('api/connexion-chauffeur/', views.connexion_chauffeur),
    path('api/initier-paiement/<int:chauffeur_id>/', views.initier_paiement),
    path('api/update-chauffeur/<int:chauffeur_id>/', views.update_chauffeur),
    path('api/profil-chauffeur/<int:chauffeur_id>/', views.profil_chauffeur),
    path('api/taxis-actifs/', views.liste_taxis_actifs),
]

# CONFIGURATION POUR LES IMAGES (MEDIA)
# Cette partie permet de servir les fichiers téléchargés pendant le développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)