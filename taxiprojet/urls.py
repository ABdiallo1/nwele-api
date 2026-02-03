from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from chauffeurs.views import (
    creer_admin_force, 
    ChauffeurListView, 
    ChauffeurProfilView, 
    PaiementChauffeurView, 
    PaytechCallbackView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/', admin.site.path),
    # Configuration
    path('api/setup-admin/', creer_admin_force),
    
    # API Chauffeurs
    path('api/chauffeurs/', ChauffeurListView.as_view()),
    path('api/chauffeurs/<int:pk>/', ChauffeurProfilView.as_view()),
    
    # Paiement (C'est ce lien que tu utiliseras)
    path('api/payer/<int:chauffeur_id>/', PaiementChauffeurView, name='payer_abonnement'),
    path('api/paiement/callback/', PaytechCallbackView.as_view(), name='paytech_callback'),
]

# C'est cette partie qui affiche les photos !
if settings.DEBUG or True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)