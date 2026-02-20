from django.contrib import admin # Ajoute cette ligne
from django.urls import path
from chauffeurs import views

urlpatterns = [
    path('admin/', admin.site.urls), # REMETS CETTE LIGNE
    path('api/connexion-chauffeur/', views.connexion_chauffeur),
    path('api/initier-paiement/<int:chauffeur_id>/', views.initier_paiement),
    path('api/update-chauffeur/<int:chauffeur_id>/', views.update_chauffeur),
    path('api/profil-chauffeur/<int:chauffeur_id>/', views.profil_chauffeur),
    path('api/taxis-actifs/', views.liste_taxis_actifs),
    path('api/webhook-fedapay/', views.fedapay_webhook),
]