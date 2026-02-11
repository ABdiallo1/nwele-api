import os, requests, json
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Chauffeur
from rest_framework.views import APIView

@api_view(['POST'])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone', '').replace(" ", "")
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        return Response({
            "id": chauffeur.id,
            "nom_complet": chauffeur.nom_complet,
            "telephone": chauffeur.telephone,
            "est_actif": chauffeur.est_actif
        }, status=200)
    except Chauffeur.DoesNotExist:
        return Response({"error": "Chauffeur non trouvé"}, status=404)

@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    num_propre = "".join(filter(str.isdigit, str(chauffeur.telephone)))
    
    PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"
    ref_command = f"PAY-{chauffeur.id}-{int(timezone.now().timestamp())}"
    
    api_key = os.getenv("PAYTECH_API_KEY", "CLE_PAR_DEFAUT_SI_VIDE")
    api_secret = os.getenv("PAYTECH_API_SECRET", "SECRET_PAR_DEFAUT_SI_VIDE")

    payload = {
        "item_name": "Abonnement N'WELE",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": ref_command,
        "command_name": f"Paiement {chauffeur.nom_complet}",
        "env": "test", 
        "customer_phone": num_propre,
        "success_url": "https://nwele-api.onrender.com/success/",
        "ipn_url": "https://nwele-api.onrender.com/api/paiement/callback/",
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "API_KEY": api_key,
        "API_SECRET": api_secret
    }

    try:
        r = requests.post(PAYTECH_URL, json=payload, headers=headers, timeout=15)
        data = r.json()
        if data.get('success') == 1:
            return Response({"url": data['redirect_url']}, status=200)
        return Response({"error": "Paytech Refusé", "details": data}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

class PaytechCallbackView(APIView):
    def post(self, request):
        # Logique pour recevoir la notification de Paytech et activer le chauffeur
        # À implémenter selon tes besoins de validation IPN
        return Response({"status": "received"}, status=200)

@api_view(['POST'])
def mettre_a_jour_chauffeur(request, pk):
    # Logique de mise à jour GPS
    return Response({"status": "updated"})

# Fonctions additionnelles pour l'admin force
from django.http import HttpResponse
def creer_admin_force(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@nwele.com', 'Parser1234')
        return HttpResponse("Admin créé !")
    return HttpResponse("Admin existe déjà.")