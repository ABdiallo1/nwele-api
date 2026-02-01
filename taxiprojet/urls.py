from django.urls import path, include
from rest_framework.routers import DefaultRouter
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

# Utilisation du Router pour l'administration DRF
router = DefaultRouter()
router.register(r'chauffeurs-admin', ChauffeurViewSet)

urlpatterns = [
    # --- Administration ---
    path('', include(router.urls)),

    # --- Espace Client (Passager) ---
    path('liste-taxis/', liste_taxis, name='liste_taxis'),

    # --- Espace Chauffeur ---
    path('connexion-chauffeur/', connexion_chauffeur, name='connexion_chauffeur'),
    path('profil-chauffeur/<int:pk>/', profil_chauffeur, name='profil_chauffeur'),
    path('mettre-a-jour-chauffeur/<int:pk>/', mettre_a_jour_chauffeur, name='mettre_a_jour_chauffeur'),

    # --- Système de Paiement PayTech ---
    # C'est cette URL que Flutter appelle pour obtenir le lien de paiement
    path('creer-lien-paytech/', creer_lien_paytech, name='creer_lien_paytech'),
    
    # URL de retour (Success URL) : affichage simple pour le chauffeur
    path('verifier-statut/<int:id>/', verifier_statut, name='verifier_statut'),
    
    # URL IPN (Webhook) : LA PLUS IMPORTANTE. PayTech appelle cette URL pour valider l'argent
    path('paytech-webhook/', paytech_webhook, name='paytech_webhook'),
    
    # Utilitaire pour valider un paiement manuellement depuis l'admin ou navigateur
    path('valider-manuel/<int:chauffeur_id>/', valider_paiement_manuel, name='valider_paiement_manuel'),
]