from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChauffeurViewSet

router = DefaultRouter()
router.register(r'liste-taxis', ChauffeurViewSet, basename='chauffeur')

urlpatterns = [
    path('', include(router.urls)),
]

