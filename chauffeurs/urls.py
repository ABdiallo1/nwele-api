from django.urls import path
from . import views

urlpatterns = [
    # Authentification & Profil
    path('api/connexion-chauffeur/', views.connexion_chauffeur, name='connexion_chauffeur'),
    path('api/profil-chauffeur/<int:chauffeur_id>/', views.profil_chauffeur, name='profil_chauffeur'),
    
    # Paiement Orange Money
    path('api/initier-paiement-orange/<int:chauffeur_id>/', views.initier_paiement_orange, name='initier_orange'),
    path('api/orange-webhook/', views.orange_webhook, name='orange_webhook'),
    path('api/paiement-reussi/', views.paiement_reussi, name='paiement_reussi'),
    
    # Gestion Chauffeur & GPS
    path('api/mettre-a-jour-chauffeur/<int:chauffeur_id>/', views.update_chauffeur, name='update_chauffeur'),
    path('api/taxis-actifs/', views.liste_taxis_actifs, name='liste_taxis_actifs'),
]