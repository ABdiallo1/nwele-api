from django.urls import path
from . import views

urlpatterns = [
    path('connexion-chauffeur/', views.connexion_chauffeur, name='connexion-chauffeur'),
    path('chauffeurs/', views.ChauffeurListView.as_view(), name='chauffeur-liste'),
    path('chauffeurs/<int:pk>/', views.ChauffeurProfilView.as_view(), name='chauffeur-profil'),
    path('mettre-a-jour-chauffeur/<int:pk>/', views.mettre_a_jour_chauffeur, name='maj-chauffeur'),

    # --- CORRECTION ICI ---
    # Supprime ".as_view()" car PaiementChauffeurView est une fonction simple (@api_view)
    path('payer/<int:chauffeur_id>/', views.PaiementChauffeurView, name='chauffeur-payer'),
    
    # Garde ".as_view()" ici car PaytechCallbackView est une classe (class APIView)
    path('paiement/callback/', views.PaytechCallbackView.as_view(), name='paytech-callback'),

    path('setup-admin/', views.creer_admin_force, name='setup-admin'),
]