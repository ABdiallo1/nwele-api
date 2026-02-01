from django.urls import path
from .views import creer_lien_paytech, paytech_webhook

urlpatterns = [
    path('creer-lien-paytech/', creer_lien_paytech),
    path('paytech-webhook/', paytech_webhook),
]