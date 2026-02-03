from django.urls import path
from . import views # Importation globale pour éviter les oublis

urlpatterns = [
    # --- AUTHENTICATION & CONNEXION ---
    # Cette route correspond à : baseUrl + /api/connexion-chauffeur/
    path('connexion-chauffeur/', views.connexion_chauffeur, name='connexion-chauffeur'),
    
    # --- API CHAUFFEURS (CARTE & PROFIL) ---
    # Pour la carte client
    path('chauffeurs/', views.ChauffeurListView.as_view(), name='chauffeur-liste'),
    # Pour voir un profil spécifique
    path('chauffeurs/<int:pk>/', views.ChauffeurProfilView.as_view(), name='chauffeur-profil'),
    
    # --- MISE À JOUR TEMPS RÉEL ---
    # Pour envoyer la position GPS et le statut en ligne depuis l'app chauffeur
    path('mettre-a-jour-chauffeur/<int:pk>/', views.mettre_a_jour_chauffeur, name='maj-chauffeur'),

    # --- PAIEMENT PAYTECH ---
    # L'app Flutter appelle : /api/payer/ID/
    path('payer/<int:chauffeur_id>/', views.PaiementChauffeurView, name='chauffeur-payer'),
    # Le serveur PayTech appelle cette route en arrière-plan
    path('paiement/callback/', views.PaytechCallbackView.as_view(), name='paytech-callback'),

    # --- UTILITAIRES ---
    path('setup-admin/', views.creer_admin_force, name='setup-admin'),
]