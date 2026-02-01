from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChauffeurViewSet, liste_taxis, connexion_chauffeur, 
    profil_chauffeur, mettre_a_jour_chauffeur, 
    creer_lien_paytech, paytech_webhook, 
    verifier_statut, valider_paiement_manuel
)

router = DefaultRouter()
router.register(r'chauffeurs-admin', ChauffeurViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('liste-taxis/', liste_taxis, name='liste_taxis'),
    path('connexion-chauffeur/', connexion_chauffeur, name='connexion_chauffeur'),
    path('profil-chauffeur/<int:pk>/', profil_chauffeur, name='profil_chauffeur'),
    path('mettre-a-jour-chauffeur/<int:pk>/', mettre_a_jour_chauffeur, name='mettre_a_jour_chauffeur'),
    path('creer-lien-paytech/', creer_lien_paytech, name='creer_lien_paytech'),
    path('verifier-statut/<int:id>/', verifier_statut, name='verifier_statut'),
    path('paytech-webhook/', paytech_webhook, name='paytech_webhook'),
    path('valider-manuel/<int:chauffeur_id>/', valider_paiement_manuel, name='valider_paiement_manuel'),
]