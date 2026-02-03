from django.urls import path
from . import views

urlpatterns = [
    # Authentification
    path('connexion-chauffeur/', views.connexion_chauffeur, name='connexion-chauffeur'),
    
    # Carte et Profils
    path('chauffeurs/', views.ChauffeurListView.as_view(), name='chauffeur-liste'),
    path('chauffeurs/<int:pk>/', views.ChauffeurProfilView.as_view(), name='chauffeur-profil'),
    
    # Mise à jour Temps Réel (GPS)
    path('mettre-a-jour-chauffeur/<int:pk>/', views.mettre_a_jour_chauffeur, name='maj-chauffeur'),

    # Paiement PayTech
    path('payer/<int:chauffeur_id>/', views.PaiementChauffeurView, name='chauffeur-payer'),
    path('paiement/callback/', views.PaytechCallbackView.as_view(), name='paytech-callback'),

    # Setup
    path('setup-admin/', views.creer_admin_force, name='setup-admin'),
]