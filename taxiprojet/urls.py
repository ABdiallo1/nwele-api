from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # On inclut les URLs de l'application chauffeurs
    path('', include('chauffeurs.urls')), 
]

# Indispensable pour voir les photos du permis et de la voiture
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Sur Render, on ajoute aussi cette ligne pour servir les images en production
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)