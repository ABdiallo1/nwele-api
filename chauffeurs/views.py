import os
import requests
import uuid
import json
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Chauffeur
from .serializers import ChauffeurSerializer

OM_AUTH_HEADER_BASIC = "Basic MmJPd1RVTDlkZnFKd1VXM1VvbXNUUHlsN2doMnJsMTQ6OXliSWhpbjJnendmSEYyc21SeVpCdklIR1hXRlM5ZVV0cjlYZTFyUklKVFA="
OM_MERCHANT_KEY = "101350" 

TOKEN_URL = "https://api.orange.com/oauth/v2/token"
PAYMENT_URL = "https://api.orange.com/orange-money-webpay/dev/v1/webpayments"

def get_orange_token():
    headers = {
        "Authorization": OM_AUTH_HEADER_BASIC,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    try:
        response = requests.post(TOKEN_URL, headers=headers, data=data, timeout=15)
        return response.json().get("access_token")
    except:
        return None

@api_view(['POST'])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone')
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        serializer = ChauffeurSerializer(chauffeur, context={'request': request})
        return Response(serializer.data)
    except Chauffeur.DoesNotExist:
        return Response({"error": "Chauffeur non trouvé"}, status=404)

@api_view(['GET'])
def profil_chauffeur(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    serializer = ChauffeurSerializer(chauffeur, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
def update_chauffeur(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    serializer = ChauffeurSerializer(chauffeur, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def liste_taxis_actifs(request):
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    serializer = ChauffeurSerializer(taxis, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
def initier_paiement_orange(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    token = get_orange_token()
    if not token:
        return Response({"error": "Auth Orange échouée"}, status=401)

    order_id = f"NW{chauffeur.id}X{uuid.uuid4().hex[:4]}"
    payload = {
        "merchant_key": OM_MERCHANT_KEY,
        "currency": "OUV",
        "order_id": order_id,
        "amount": 100,
        "return_url": "https://nwele-api.onrender.com/api/paiement-reussi/",
        "cancel_url": "https://nwele-api.onrender.com/api/paiement-annule/",
        "notif_url": "https://nwele-api.onrender.com/api/orange-webhook/",
        "lang": "fr",
        "reference": "Activation Nwele"
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        response = requests.post(PAYMENT_URL, json=payload, headers=headers, timeout=20)
        data = response.json()
        if "payment_url" in data:
            return Response({'url': data['payment_url']})
        return Response({'error': "Refus Orange", 'details': data}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@csrf_exempt
def orange_webhook(request):
    try:
        data = json.loads(request.body)
        if data.get('status') == 'SUCCESS':
            order_id = data.get('order_id')
            chauffeur_id = order_id.split('NW')[1].split('X')[0]
            chauffeur = Chauffeur.objects.get(id=int(chauffeur_id))
            chauffeur.est_actif = True
            chauffeur.save()
    except:
        pass
    return HttpResponse("OK", status=200)

def paiement_reussi(request):
    return HttpResponse("<h1 style='color:green;text-align:center;'>Paiement réussi !</h1>")