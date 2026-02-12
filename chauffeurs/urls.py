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
    # --- AUTHENTIFICATION ---
    # Utilisé par EcranLoginChauffeur pour vérifier le numéro
    path('connexion-chauffeur/', connexion_chauffeur, name='connexion_chauffeur'),

    # --- PROFIL & SERVICES ---
    # Utilisé par EcranProfil et EcranDashboard pour récupérer les infos (nom, jours restants)
    path('profil-chauffeur/<int:pk>/', ChauffeurProfilView.as_view(), name='profil_chauffeur'),
    
    # Utilisé par le Dashboard pour envoyer la position GPS et le statut "En ligne/Hors ligne"
    path('mettre-a-jour-chauffeur/<int:pk>/', mettre_a_jour_chauffeur, name='mettre_a_jour_chauffeur'),

    # --- PAIEMENT ---
    # Génère le lien de paiement PayTech
    path('payer/<int:chauffeur_id>/', PaiementChauffeurView, name='payer_abonnement'),
    
    # Reçoit la confirmation de paiement automatique de PayTech (IPN)
    path('paiement/callback/', PaytechCallbackView.as_view(), name='callback_paytech'),

    # --- CLIENTS (CARTE) ---
    # Utilisé par l'application Client pour voir tous les taxis actifs sur la carte
    path('liste-taxis/', ChauffeurListView.as_view(), name='liste_taxis_actifs'),
]