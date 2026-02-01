from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import HttpResponse

# L'import relatif (.) est la solution pour Render
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

# Configuration du Router pour les vues d'administration (ModelViewSet)
router = DefaultRouter()
router.register(r'chauffeurs-admin', ChauffeurViewSet)

urlpatterns = [
    # Route racine pour l'administration des chauffeurs
    path('', include(router.urls)),
    
    # Routes Espace Client
    path('liste-taxis/', liste_taxis, name='liste_taxis'),
    
    # Routes Espace Chauffeur
    path('connexion-chauffeur/', connexion_chauffeur, name='connexion_chauffeur'),
    path('profil-chauffeur/<int:pk>/', profil_chauffeur, name='profil_chauffeur'),
    path('mettre-a-jour-chauffeur/<int:pk>/', mettre_a_jour_chauffeur, name='mettre_a_jour_chauffeur'),
    
    # Routes Système de Paiement PayTech
    path('creer-lien-paytech/', creer_lien_paytech, name='creer_lien_paytech'),
    path('paytech-webhook/', paytech_webhook, name='paytech_webhook'),
    path('verifier-statut/<int:id>/', verifier_statut, name='verifier_statut'),
    
    # Route de secours / Manuelle
    path('valider-manuel/<int:chauffeur_id>/', valider_paiement_manuel, name='valider_paiement_manuel'),
]