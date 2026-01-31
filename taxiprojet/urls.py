from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from chauffeurs import views 

urlpatterns = [
    # 1. Interface d'administration Django
    path('admin/', admin.site.urls),

    # 2. ESPACE CLIENT (PASSAGER)
    path('api/liste-taxis/', views.liste_taxis, name='liste_taxis'),

    # 3. ESPACE CHAUFFEUR (PROFIL & CONNEXION)
    path('api/connexion-chauffeur/', views.connexion_chauffeur, name='connexion_chauffeur'),
    path('api/profil-chauffeur/<int:pk>/', views.profil_chauffeur, name='profil_chauffeur'),
    path('api/mettre-a-jour-chauffeur/<int:pk>/', views.mettre_a_jour_chauffeur, name='mettre_a_jour_chauffeur'),
    path('api/creer-chauffeur/', views.creer_chauffeur_manuel, name='creer_chauffeur_manuel'),
    path('api/deconnexion-chauffeur/<int:pk>/', views.deconnexion_chauffeur, name='deconnexion_chauffeur'),

    # 4. SYSTÈME DE PAIEMENT & ABONNEMENT (IPN & Redirection)
    path('api/creer-lien-orange-money/', views.creer_lien_orange_money, name='creer_paiement'),
    path('api/verifier-statut/<int:id>/', views.verifier_statut, name='verifier_statut'),
    path('api/paytech-webhook/', views.paytech_webhook, name='paytech_webhook'),
    path('api/valider-chauffeur/<int:chauffeur_id>/', views.valider_paiement_manuel, name='valider_manuel'),

    # 5. ADMINISTRATION API (REST Framework ViewSet)
    path('api/chauffeurs-all/', views.ChauffeurViewSet.as_view({
        'get': 'list', 
        'post': 'create'
    }), name='chauffeurs_list_drf'),
    
    path('api/chauffeurs-all/<int:pk>/', views.ChauffeurViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='chauffeur_detail_drf'),
] 

# --- GESTION DES FICHIERS MÉDIAS ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)