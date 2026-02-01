from django.urls import path, include
from rest_framework.routers import DefaultRouter

# L'import relatif (.) garantit que Django trouve views.py dans le même dossier
from .views import (
    ChauffeurViewSet, 
    liste_taxis, 
    connexion_chauffeur, 
    profil_chauffeur, 
    mettre_a_jour_chauffeur, 
    creer_lien_paytech, 
    paytech_webhook, 
    verifier_statut, 
    valider_paiement_manuel
)


# Configuration du Router pour les vues d'administration automatique (DRF)
router = DefaultRouter()
router.register(r'chauffeurs-admin', ChauffeurViewSet)

urlpatterns = [
    # 1. Routes de l'API d'administration (CRUD)
    path('', include(router.urls)),
    
    # 2. Routes Espace Client (Passager)
    path('liste-taxis/', liste_taxis, name='liste_taxis'),
    
    # 3. Routes Espace Chauffeur (Profil & Connexion)
    path('connexion-chauffeur/', connexion_chauffeur, name='connexion_chauffeur'),
    path('profil-chauffeur/<int:pk>/', profil_chauffeur, name='profil_chauffeur'),
    path('mettre-a-jour-chauffeur/<int:pk>/', mettre_a_jour_chauffeur, name='mettre_a_jour_chauffeur'),
    
    # 4. Routes Système de Paiement PayTech
    path('creer-lien-paytech/', creer_lien_paytech, name='creer_lien_paytech'),
    path('paytech-webhook/', paytech_webhook, name='paytech_webhook'),
    path('verifier-statut/<int:id>/', verifier_statut, name='verifier_statut'),
    
    # 5. Route de secours (Validation manuelle par l'admin)
    path('valider-manuel/<int:chauffeur_id>/', valider_paiement_manuel, name='valider_paiement_manuel'),
    path('admin/', admin.site.urls), # C'est cette ligne qui ouvre l'accès
    path('api/', include('api.urls')),
    path('', include(router.urls)),
    path('liste-taxis/', liste_taxis),
    path('creer-lien-paytech/', creer_lien_paytech),
    path('paytech-webhook/', paytech_webhook),
    path('verifier-statut/<int:id>/', verifier_statut),
]