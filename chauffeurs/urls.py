from django.urls import path
from . import views

urlpatterns = [
    path('force-migrate/', views.force_migrate),
    path('creer-admin-nwele/', views.creer_admin_force),
    path('connexion-chauffeur/', views.connexion_chauffeur),
    path('profil-chauffeur/<int:pk>/', views.ChauffeurProfilView),
    path('payer/<int:chauffeur_id>/', views.PaiementChauffeurView),
    path('paiement/callback/', views.PaytechCallbackView),
    path('paiement-succes/', views.paiement_succes),
    path('chauffeur/update/<int:pk>/', views.mettre_a_jour_chauffeur),
    path('chauffeurs-actifs/', views.ChauffeurListView),
]