from django.urls import path
from . import views

urlpatterns = [
    path('connexion-chauffeur/', views.connexion_chauffeur, name='connexion_chauffeur'),
    path('initier-paiement/<int:chauffeur_id>/', views.initier_paiement, name='initier_paiement'),
    path('fedapay-webhook/', views.fedapay_webhook, name='fedapay_webhook'),
    path('profil-chauffeur/<int:chauffeur_id>/', views.profil_chauffeur, name='profil_chauffeur'),
    path('update-chauffeur/<int:chauffeur_id>/', views.update_chauffeur, name='update_chauffeur'),
    path('taxis-actifs/', views.liste_taxis_actifs, name='liste_taxis_actifs'),
]