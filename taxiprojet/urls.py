from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
from chauffeurs.views import creer_admin_force

urlpatterns = [
    # Interface d'administration Django
    path('admin/', admin.site.urls),
    
    # Inclusion des routes de ton application chauffeurs
    path('api/', include('chauffeurs.urls')), 
    
    # URL de secours pour créer l'admin si la base SQLite est réinitialisée
    path('creer-admin-nwele/', creer_admin_force),
]

# Gestion des fichiers statiques et médias
if settings.DEBUG:
    # En mode développement local
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Configuration spécifique pour Render en mode production (DEBUG = False)
    # Cela permet à Django de "servir" les images lui-même
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]