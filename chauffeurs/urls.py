from django.urls import path
from .views import (
    connexion_chauffeur, 
    PaiementChauffeurView, 
    PaytechCallbackView,
    mettre_a_jour_chauffeur, # Maintenant cette fonction existe dans views.py
    ChauffeurListView, 
    ChauffeurProfilView, 
    paiement_succes
)

urlpatterns = [
    path('connexion-chauffeur/', connexion_chauffeur),
    path('payer/<int:chauffeur_id>/', PaiementChauffeurView),
    path('paiement/callback/', PaytechCallbackView),
    path('mettre-a-jour-chauffeur/<int:pk>/', mettre_a_jour_chauffeur),
    path('liste-taxis/', ChauffeurListView),
    path('profil-chauffeur/<int:pk>/', ChauffeurProfilView),
    path('paiement-succes/', paiement_succes),
]