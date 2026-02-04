from django.urls import path
from .views import (
    connexion_chauffeur, 
    PaiementChauffeurView, 
    PaytechCallbackView,
    mettre_a_jour_chauffeur,
    ChauffeurListView,
    ChauffeurProfilView
)

urlpatterns = [
    # Route pour la connexion : /api/connexion-chauffeur/
    path('connexion-chauffeur/', connexion_chauffeur, name='connexion'),
    
    # Route pour initier le paiement : /api/payer/ID/
    path('payer/<int:chauffeur_id>/', PaiementChauffeurView, name='payer'),
    
    # Route pour le retour PayTech (IPN) : /api/paiement/callback/
    path('paiement/callback/', PaytechCallbackView.as_view(), name='callback_paytech'),
    
    # Mise à jour GPS : /api/mettre-a-jour-chauffeur/ID/
    path('mettre-a-jour-chauffeur/<int:pk>/', mettre_a_jour_chauffeur, name='update_gps'),
    
    # Liste des taxis pour les clients : /api/liste-taxis/
    path('liste-taxis/', ChauffeurListView.as_view(), name='liste_taxis'),
    
    # Détails d'un profil : /api/chauffeurs/ID/
    path('chauffeurs/<int:pk>/', ChauffeurProfilView.as_view(), name='profil_chauffeur'),
]