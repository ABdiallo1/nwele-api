from django.urls import path
from . import views

urlpatterns = [
    # --- AUTHENTIFICATION ---
    # Pour la connexion initiale du chauffeur
    path('api/connexion-chauffeur/', views.connexion_chauffeur, name='connexion_chauffeur'),
    
    # Pour récupérer les infos d'un chauffeur spécifique
    path('api/profil-chauffeur/<int:chauffeur_id>/', views.profil_chauffeur, name='profil_chauffeur'),

    # --- PAIEMENT PAYTECH (Orange Money / Mobicash) ---
    # Pour générer le lien de paiement PayTech
    path('api/initier-paiement-paytech/<int:chauffeur_id>/', views.initier_paiement_paytech, name='initier_paytech'),
    
    # URL secrète que PayTech appelle pour confirmer le paiement
    path('api/paytech-webhook/', views.paytech_webhook, name='paytech_webhook'),
    
    # Page de confirmation affichée dans le navigateur après succès
    path('api/paiement-reussi/', views.paiement_reussi, name='paiement_reussi'),

    # --- GPS ET CARTOGRAPHIE ---
    # Pour mettre à jour la position GPS du chauffeur (toutes les 30s)
    path('api/update-chauffeur/<int:chauffeur_id>/', views.update_chauffeur, name='update_chauffeur'),
    
    # Pour que l'application Client récupère les taxis à Bamako
    path('api/taxis-actifs/', views.liste_taxis_actifs, name='taxis_actifs'),
    
    # Route de secours pour la liste complète
    path('api/liste-taxis/', views.liste_taxis_actifs, name='liste_taxis'),
]