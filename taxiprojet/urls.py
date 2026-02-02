from django.contrib import admin
from django.urls import path
from chauffeurs.views import (
    creer_admin_force, 
    ChauffeurListView, 
    ChauffeurProfilView, 
    PaiementChauffeurView, 
    PaytechCallbackView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Configuration
    path('api/setup-admin/', creer_admin_force),
    
    # API Chauffeurs
    path('api/chauffeurs/', ChauffeurListView.as_view()),
    path('api/chauffeurs/<int:pk>/', ChauffeurProfilView.as_view()),
    
    # Paiement (C'est ce lien que tu utiliseras)
    path('api/payer/<int:chauffeur_id>/', PaiementChauffeurView, name='payer_abonnement'),
    path('api/paiement/callback/', PaytechCallbackView.as_view(), name='paytech_callback'),
]