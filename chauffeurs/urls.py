from django.urls import path
from . import views

urlpatterns = [
    path('api/connexion-chauffeur/', views.connexion_chauffeur, name='connexion_chauffeur'),
    path('api/profil-chauffeur/<int:chauffeur_id>/', views.profil_chauffeur, name='profil_chauffeur'),
    path('api/initier-paiement-maishapay/<int:chauffeur_id>/', views.initier_paiement_maishapay, name='initier_maishapay'),
    path('api/maishapay-webhook/', views.maishapay_webhook, name='maishapay_webhook'),
    path('api/mettre-a-jour-chauffeur/<int:chauffeur_id>/', views.update_chauffeur, name='update_chauffeur'),
    path('api/taxis-actifs/', views.liste_taxis_actifs, name='liste_taxis_actifs'),
    path('api/paiement-reussi/', views.paiement_reussi, name='paiement_reussi'),
]