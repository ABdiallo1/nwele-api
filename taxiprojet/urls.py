from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from chauffeurs.views import creer_admin_force

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chauffeurs.urls')), 
    path('creer-admin-nwele/', creer_admin_force),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)