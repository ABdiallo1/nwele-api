from django.contrib import admin
from django.urls import path
from chauffeurs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/connexion-chauffeur/', views.connexion_chauffeur),
    path('api/initier-paiement/<int:chauffeur_id>/', views.initier_paiement),
    path('api/update-chauffeur/<int:chauffeur_id>/', views.update_chauffeur), # BIEN VERIFIER CETTE LIGNE
    path('api/profil-chauffeur/<int:chauffeur_id>/', views.profil_chauffeur),
    path('api/taxis-actifs/', views.liste_taxis_actifs),
]