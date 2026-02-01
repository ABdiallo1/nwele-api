from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Vues de base (API & Carte)
    ChauffeurListView, 
    
    # Vues d'authentification et gestion
    connexion_chauffeur, 
    profil_chauffeur, 
    mettre_a_jour_chauffeur, 
    
    # Vues de paiement PayTech
    PaiementChauffeurView, 
    PaytechCallbackView,
    
    # Utilitaires
    verifier_statut
)

# On garde le router pour l'interface d'administration automatique (si utilisée)
router = DefaultRouter()
# Note: Assure-toi que ChauffeurViewSet est bien défini dans tes views.py
# router.register(r'chauffeurs-admin', ChauffeurViewSet) 

urlpatterns = [
    # 1. Routes API pour la carte et l'application Flutter
    path('liste/', ChauffeurListView.as_view(), name='chauffeur-liste'),
    
    # 2. Gestion du compte Chauffeur
    path('connexion/', connexion_chauffeur, name='connexion_chauffeur'),
    path('profil/<int:pk>/', profil_chauffeur, name='profil_chauffeur'),
    path('maj-profil/<int:pk>/', mettre_a_jour_chauffeur, name='mettre_a_jour_chauffeur'),
    path('verifier-statut/<int:id>/', verifier_statut, name='verifier_statut'),

    # 3. Système de paiement PayTech
    # Cette route génère le lien de paiement
    path('payer/<int:chauffeur_id>/', PaiementChauffeurView.as_view(), name='chauffeur-payer'),
    
    # Cette route reçoit la confirmation de PayTech (Webhook/IPN)
    path('paiement/callback/', PaytechCallbackView.as_view(), name='paytech-callback'),

    # 4. Inclusion des routes du router (si nécessaire)
    path('admin-api/', include(router.urls)),
    path('setup-admin/', creer_admin_force),
    path('profil/<int:pk>/', ChauffeurProfilView.as_view()),
]