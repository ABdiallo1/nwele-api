from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from chauffeurs.views import creer_admin_force

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chauffeurs.urls')), 
    path('creer-admin-nwele/', creer_admin_force),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]