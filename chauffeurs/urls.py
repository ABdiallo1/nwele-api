from django.urls import path
from . import views

urlpatterns = [
    # --- AUTHENTICATION & PROFIL ---
    # Pour la connexion initiale
    path('api/connexion-chauffeur/', views.connexion_chauffeur, name='connexion_chauffeur'),
    # Pour vérifier si le compte est actif (utilisé par le bouton "ACTIVER")
    path('api/profil-chauffeur/<int:pk>/', views.ChauffeurProfilView, name='profil_chauffeur'),

    # --- PAIEMENT PAYTECH ---
    # Pour générer le lien de paiement
    path('api/payer/<int:chauffeur_id>/', views.PaiementChauffeurView, name='payer_abonnement'),
    # URL de notification (IPN) que Paytech appelle en secret pour valider l'abonnement
    path('api/paiement/callback/', views.PaytechCallbackView, name='paytech_callback'),
    # URL de redirection après succès (affichage d'un message HTML simple)
    path('api/paiement-succes/', views.paiement_succes, name='paiement_succes'),

    # --- DASHBOARD & SERVICE ---
    # Pour activer/désactiver le bouton "EN SERVICE" et mettre à jour la position
    path('api/chauffeur/update/<int:pk>/', views.mettre_a_jour_chauffeur, name='update_chauffeur'),
    # Pour afficher les chauffeurs sur la carte (côté client)
    path('api/chauffeurs-actifs/', views.ChauffeurListView, name='chauffeurs_actifs'),

    # --- UTILITAIRES ---
    # Pour créer l'admin si tu as perdu l'accès
    path('api/admin-setup-force/', views.creer_admin_force, name='creer_admin_force'),
]