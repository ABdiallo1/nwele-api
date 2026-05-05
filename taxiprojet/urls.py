from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chauffeurs.urls')), 
]

# Servir les fichiers statiques (CSS, JS)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Servir les médias (Images de profil, permis)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Correction cruciale pour Render : re_path pour servir les images
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]