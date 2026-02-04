from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve # Pour servir les médias même hors DEBUG si besoin
from django.urls import re_path
from chauffeurs.views import creer_admin_force

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Toutes les routes commençant par /api/ iront chercher dans chauffeurs/urls.py
    path('api/', include('chauffeurs.urls')), 
    
    # Route de secours pour créer le super-utilisateur sur Render
    path('creer-admin-nwele/', creer_admin_force),
]

# Gestion des fichiers médias (Photos permis/voitures)
# En mode DEBUG et en production sur Render
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Configuration pour servir les fichiers médias en production sur Render
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]