from django.urls import path
from . import views

urlpatterns = [
    # Connexion et Profil
    path('api/connexion-chauffeur/', views.connexion_chauffeur, name='connexion_chauffeur'),
    path('api/profil-chauffeur/<int:chauffeur_id>/', views.profil_chauffeur, name='profil_chauffeur'),
    
    # MaishaPay (Nouveau système)
    path('api/initier-paiement-maishapay/<int:chauffeur_id>/', views.initier_paiement_maishapay, name='initier_maishapay'),
    path('api/maishapay-webhook/', views.maishapay_webhook, name='maishapay_webhook'),
    
    # Mise à jour et Taxis
    path('api/mettre-a-jour-chauffeur/<int:chauffeur_id>/', views.update_chauffeur, name='update_chauffeur'),
    path('api/taxis-actifs/', views.liste_taxis_actifs, name='liste_taxis_actifs'),
    
    # Page de retour
    path('api/paiement-reussi/', views.paiement_reussi, name='paiement_reussi'),
]