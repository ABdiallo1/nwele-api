from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
from chauffeurs.views import creer_admin_force

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chauffeurs.urls')), 
    path('creer-admin-nwele/', creer_admin_force),
]

# Gestion des médias pour Render (Production)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]