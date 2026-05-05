from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import re

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chauffeurs.urls')), 
]

# Configuration pour servir les médias (images) sur Render et en local
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Cette ligne permet de servir les images même si DEBUG=False
    urlpatterns += [
        path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)