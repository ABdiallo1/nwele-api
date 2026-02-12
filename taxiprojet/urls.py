from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from chauffeurs.views import creer_admin_force

urlpatterns = [
    # Interface d'administration Django
    path('admin/', admin.site.urls),

    # Inclusion des routes de ton application Chauffeurs
    # Toutes tes URLs seront accessibles via : https://nwele-api.onrender.com/api/...
    path('api/', include('chauffeurs.urls')), 

    # Route spéciale pour créer l'admin si tu perds tes accès sur Render
    path('creer-admin-nwele/', creer_admin_force),
]

# --- GESTION DES FICHIERS STATIQUES ET MÉDIAS ---
# Cette configuration est cruciale pour que Render affiche les photos de permis/véhicules
if settings.DEBUG:
    # Mode Développement
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Mode Production (Render) : On utilise 'serve' pour forcer l'affichage des fichiers
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]