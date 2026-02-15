from django.urls import path
from . import views

urlpatterns = [
    path('api/connexion-chauffeur/', views.connexion_chauffeur),
    path('api/payer/<int:chauffeur_id>/', views.initier_paiement),
    path('api/paytech-callback/', views.paytech_callback),
    path('api/profil-chauffeur/<int:chauffeur_id>/', views.profil_chauffeur),
    path('api/chauffeur/update/<int:chauffeur_id>/', views.update_chauffeur),
]