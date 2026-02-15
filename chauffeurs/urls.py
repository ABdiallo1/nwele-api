from django.urls import path
from . import views

urlpatterns = [
    # Connexion et profil
    path('connexion-chauffeur/', views.connexion_chauffeur),
    path('profil-chauffeur/<int:chauffeur_id>/', views.profil_chauffeur),
    
    # Paiement PayTech
    path('payer/<int:chauffeur_id>/', views.initier_paiement),
    path('paytech-callback/', views.paytech_callback),
    
    # Mise à jour GPS
    path('chauffeur/update/<int:chauffeur_id>/', views.update_chauffeur),
]