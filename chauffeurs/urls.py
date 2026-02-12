from django.urls import path
from .views import (
    connexion_chauffeur, PaiementChauffeurView, PaytechCallbackView,
    mettre_a_jour_chauffeur, ChauffeurListView, ChauffeurProfilView
)

urlpatterns = [
    path('connexion-chauffeur/', connexion_chauffeur, name='connexion'),
    path('payer/<int:chauffeur_id>/', PaiementChauffeurView, name='payer'),
    path('paiement/callback/', PaytechCallbackView.as_view(), name='callback_paytech'),
    path('mettre-a-jour-chauffeur/<int:pk>/', mettre_a_jour_chauffeur, name='update_gps'),
    path('liste-taxis/', ChauffeurListView.as_view(), name='liste_taxis'),
    path('profil-chauffeur/<int:pk>/', ChauffeurProfilView.as_view(), name='profil_chauffeur'),
]