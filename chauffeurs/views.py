import os, requests, json
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import Chauffeur
from django.http import HttpResponse
# IMPORT MANQUANT CORRIGÉ ICI :
from django.contrib.auth.models import User 

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
    
    api_key = os.getenv("PAYTECH_API_KEY", "VOTRE_CLE")
    api_secret = os.getenv("PAYTECH_API_SECRET", "VOTRE_SECRET")

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
        "Content-Type": "application/json",
        "API_KEY": api_key,
        "API_SECRET": api_secret
    }

    try:
        response = requests.post(PAYTECH_URL, json=payload, headers=headers, timeout=15)
        res_data = response.json()
        if res_data.get('success') == 1:
            return Response({"url": res_data['redirect_url']}, status=200)
        return Response({"error": "Erreur PayTech", "details": res_data}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# URL DE SECOURS POUR L'ADMIN
def creer_admin_force(request):
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@nwele.com', 'Parser1234')
            return HttpResponse("✅ Admin créé avec succès ! Login: admin / Pass: Parser1234")
        return HttpResponse("ℹ️ L'admin existe déjà.")
    except Exception as e:
        return HttpResponse(f"❌ Erreur : {str(e)}")

class PaytechCallbackView(APIView):
    def post(self, request):
        return Response({"status": "ok"}, status=200)

@api_view(['POST'])
def mettre_a_jour_chauffeur(request, pk):
    return Response({"status": "position mise à jour"})

class ChauffeurListView(APIView):
    def get(self, request):
        return Response([])

class ChauffeurProfilView(APIView):
    def get(self, request, pk):
        chauffeur = get_object_or_404(Chauffeur, pk=pk)
        return Response({"id": chauffeur.id, "nom": chauffeur.nom_complet})