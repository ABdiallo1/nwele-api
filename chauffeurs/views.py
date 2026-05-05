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

# --- CONFIGURATION ORANGE MONEY (Tes identifiants validés) ---
# Header Authorization fourni précédemment
OM_AUTH_HEADER_BASIC = "Basic MmJPd1RVTDlkZnFKd1VXM1VvbXNUUHlsN2doMnJsMTQ6OXliSWhpbjJnendmSEYyc21SeVpCdklIR1hXRlM5ZVV0cjlYZTFyUklKVFA="

# En mode Sandbox Mali, essaye d'abord cette valeur ou ta Merchant Key si tu la reçois
OM_MERCHANT_KEY = "101350" 

TOKEN_URL = "https://api.orange.com/oauth/v2/token"
PAYMENT_URL = "https://api.orange.com/orange-money-webpay/dev/v1/webpayments"

def get_orange_token():
    """Récupère le Token d'accès (valide 1 heure comme indiqué sur ton image)"""
    headers = {
        "Authorization": OM_AUTH_HEADER_BASIC,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    try:
        response = requests.post(TOKEN_URL, headers=headers, data=data, timeout=15)
        res_data = response.json()
        return res_data.get("access_token")
    except Exception as e:
        print(f"Erreur d'obtention du Token: {e}")
        return None

# --- 1. GESTION DU CHAUFFEUR ---

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

# --- 2. LOGIQUE DE PAIEMENT ORANGE MONEY ---

@api_view(['POST'])
def initier_paiement_orange(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    
    # Récupération du Token
    token = get_orange_token()
    if not token:
        return Response({"error": "Impossible de s'authentifier auprès d'Orange."}, status=401)

    # Référence unique pour la transaction
    order_id = f"NW{chauffeur.id}X{uuid.uuid4().hex[:4]}"

    payload = {
        "merchant_key": OM_MERCHANT_KEY,
        "currency": "OUV", # Devise Sandbox pour les tests
        "order_id": order_id,
        "amount": 100,
        "return_url": "https://nwele-api.onrender.com/api/paiement-reussi/",
        "cancel_url": "https://nwele-api.onrender.com/api/paiement-annule/",
        "notif_url": "https://nwele-api.onrender.com/api/orange-webhook/",
        "lang": "fr",
        "reference": "Activation Compte Nwele"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(PAYMENT_URL, json=payload, headers=headers, timeout=20)
        data = response.json()
        
        if "payment_url" in data:
            return Response({'url': data['payment_url']})
        
        return Response({
            'error': "Orange Money a refusé l'initialisation",
            'details': data.get('message', 'Vérifiez la Merchant Key')
        }, status=400)

    except Exception as e:
        return Response({'error': f"Erreur de connexion : {str(e)}"}, status=500)

# --- 3. WEBHOOK ET CONFIRMATION ---

@csrf_exempt
def orange_webhook(request):
    """Notification de succès envoyée par Orange"""
    try:
        data = json.loads(request.body)
        if data.get('status') == 'SUCCESS':
            order_id = data.get('order_id')
            chauffeur_id = order_id.split('NW')[1].split('X')[0]
            
            chauffeur = Chauffeur.objects.get(id=int(chauffeur_id))
            chauffeur.est_actif = True
            chauffeur.save()
            return HttpResponse("OK", status=200)
    except:
        pass
    return HttpResponse("Received", status=200)

def paiement_reussi(request):
    """Affichage final après paiement"""
    return HttpResponse("""
        <div style='text-align:center; margin-top:100px; font-family:sans-serif;'>
            <h1 style='color:#FF7900;'>Orange Money</h1>
            <h2 style='color:green;'>✅ Paiement effectué avec succès !</h2>
            <p>Votre compte N'WÉLÉ est maintenant activé.</p>
        </div>
    """)