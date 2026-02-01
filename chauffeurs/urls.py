from django.urls import path
from .views import (
    creer_admin_force,
    ChauffeurListView,
    ChauffeurProfilView,
    PaiementChauffeurView,
    PaytechCallbackView
)

urlpatterns = [
    # Route de secours pour l'admin
    path('setup-admin/', creer_admin_force, name='setup-admin'),
    
    # API Chauffeurs
    path('liste/', ChauffeurListView.as_view(), name='chauffeur-liste'),
    path('profil/<int:pk>/', ChauffeurProfilView.as_view(), name='chauffeur-profil'),
    
    # Paiement
    path('payer/<int:chauffeur_id>/', PaiementChauffeurView.as_view(), name='chauffeur-payer'),
    path('paiement/callback/', PaytechCallbackView.as_view(), name='paytech-callback'),
]