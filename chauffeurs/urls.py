from django.urls import path
from . import views

urlpatterns = [
    # --- ROUTE DE SECOURS (A utiliser une seule fois) ---
    path('api/force-migrate/', views.force_migrate, name='force_migrate'),

    # --- AUTHENTICATION & PROFIL ---
    path('api/connexion-chauffeur/', views.connexion_chauffeur, name='connexion_chauffeur'),
    path('api/profil-chauffeur/<int:pk>/', views.ChauffeurProfilView, name='profil_chauffeur'),

    # --- PAIEMENT PAYTECH ---
    path('api/payer/<int:chauffeur_id>/', views.PaiementChauffeurView, name='payer_abonnement'),
    path('api/paiement/callback/', views.PaytechCallbackView, name='paytech_callback'),
    path('api/paiement-succes/', views.paiement_succes, name='paiement_succes'),

    # --- DASHBOARD & SERVICE ---
    path('api/chauffeur/update/<int:pk>/', views.mettre_a_jour_chauffeur, name='update_chauffeur'),
    path('api/chauffeurs-actifs/', views.ChauffeurListView, name='chauffeurs_actifs'),
]