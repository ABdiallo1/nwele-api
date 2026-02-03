from django.urls import path
from . import views

urlpatterns = [
    # Connexion
    path('connexion-chauffeur/', views.connexion_chauffeur, name='connexion-chauffeur'),
    
    # API Chauffeurs
    path('chauffeurs/', views.ChauffeurListView.as_view(), name='chauffeur-liste'),
    path('chauffeurs/<int:pk>/', views.ChauffeurProfilView.as_view(), name='chauffeur-profil'),
    
    # Mise à jour
    path('mettre-a-jour-chauffeur/<int:pk>/', views.mettre_a_jour_chauffeur, name='maj-chauffeur'),

    # Paiement (FONCTION : donc PAS de .as_view())
    path('payer/<int:chauffeur_id>/', views.PaiementChauffeurView, name='chauffeur-payer'),
    
    # Callback (CLASSE : donc .as_view())
    path('paiement/callback/', views.PaytechCallbackView.as_view(), name='paytech-callback'),

    # Setup
    path('setup-admin/', views.creer_admin_force, name='setup-admin'),
]