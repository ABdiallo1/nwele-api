from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from chauffeurs.views import creer_admin_force

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chauffeurs.urls')),  # Relie vers le fichier urls.py de l'application
    path('creer-admin-nwele/', creer_admin_force), # Route de secours pour créer l'admin
]

# Indispensable pour voir les photos du permis et de la voiture
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)