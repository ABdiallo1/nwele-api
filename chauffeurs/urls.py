from django.urls import path
from .views import (
    connexion_chauffeur, 
    initier_paiement, 
    paytech_callback, 
    profil_chauffeur, 
    update_chauffeur
)

urlpatterns = [
    # Connexion
    path('api/connexion-chauffeur/', connexion_chauffeur, name='connexion_chauffeur'),
    
    # Paiement PayTech
    path('api/payer/<int:chauffeur_id>/', initier_paiement, name='initier_paiement'),
    path('api/paytech-callback/', paytech_callback, name='paytech_callback'),
    
    # Profil et Vérification statut actif
    path('api/profil-chauffeur/<int:chauffeur_id>/', profil_chauffeur, name='profil_chauffeur'),
    
    # GPS et Statut en ligne (utilisé par le Dashboard Flutter)
    path('api/mettre-a-jour-chauffeur/<int:chauffeur_id>/', update_chauffeur, name='update_chauffeur'),
]