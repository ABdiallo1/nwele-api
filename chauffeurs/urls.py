from django.urls import path
from .views import connexion_chauffeur, initier_paiement, paytech_callback, profil_chauffeur, update_chauffeur

urlpatterns = [
    path('connexion-chauffeur/', connexion_chauffeur, name='connexion_chauffeur'),
    path('payer/<int:chauffeur_id>/', initier_paiement, name='initier_paiement'),
    path('paytech-callback/', paytech_callback, name='paytech_callback'),
    path('profil-chauffeur/<int:chauffeur_id>/', profil_chauffeur, name='profil_chauffeur'),
    path('mettre-a-jour-chauffeur/<int:chauffeur_id>/', update_chauffeur, name='update_chauffeur'),
]