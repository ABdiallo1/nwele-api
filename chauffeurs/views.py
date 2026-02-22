import os
import requests
import uuid
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Chauffeur
from .serializers import ChauffeurSerializer

# 1. CONNEXION
@api_view(['POST'])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone')
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        serializer = ChauffeurSerializer(chauffeur, context={'request': request})
        return Response(serializer.data)
    except Chauffeur.DoesNotExist:
        return Response({"error": "Chauffeur non trouvé"}, status=404)

# 2. PAIEMENT MAISHAPAY
@api_view(['POST'])
def initier_paiement_maishapay(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    url_maisha = "https://marchand.maishapay.online/api/collect/v2/store/card"
    
    # Tes clés Sandbox fonctionnelles
    public_key = "MP-SBPK-/yFFW4a11Pl$cHfUimIS2YaOrde$t99o.8s8uUwNyycDDIg1v3F0SdA7$OGSJWVS$7qaJPQmhKhabuZqZQRmp2s6$yhv6uC/Cc5zGEQJO$3SB0rRfKI0TUp0"
    secret_key = "MP-SBPK-B$woJen2LeuSboIeNk8XiAEy0L$1/AX73DyYdn88JjUdT2VZ1WuN4EA$25gU2wr23Au.U0kKm$7e5vsTAEqGf15.8y0fmx.JiwwGdX3oWVmyedw2vjno$O$a"

    payload = {
        "transactionReference": f"NW-{chauffeur.id}-{uuid.uuid4().hex[:6]}", 
        "gatewayMode": 0,  # 0 pour SANDBOX
        "publicApiKey": public_key,
        "secretApiKey": secret_key,
        "order": {
            "amount": "100",
            "currency": "XOF",
            "customerFullName": chauffeur.nom_complet,
            "customerPhoneNumber": chauffeur.telephone,
            "customerEmailAdress": "contact@nwele.com"
        },
        "paymentChannel": {
            "channel": "CARD",
            "provider": "VISA",
            "callbackUrl": "https://nwele-api.onrender.com/api/maishapay-webhook/"
        }
    }

    try:
        response = requests.post(url_maisha, json=payload)
        data = response.json()
        if data.get('status_code') == 202:
            return Response({'url': data['paymentPage']})
        return Response({'error': data.get('transactionDescription', 'Erreur MaishaPay')}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# 3. WEBHOOK (ACTIVATION AUTOMATIQUE)
@csrf_exempt
def maishapay_webhook(request):
    status_payment = request.GET.get('status')
    transaction_ref = request.GET.get('transactionRefId')
    
    if status_payment == "200" and transaction_ref:
        try:
            chauffeur_id = transaction_ref.split('-')[1]
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            chauffeur.est_actif = True
            chauffeur.save()
            return HttpResponse("OK")
        except:
            return HttpResponse("Erreur", status=500)
    return HttpResponse("Invalide", status=400)

# 4. AUTRES FONCTIONS
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

def paiement_reussi(request):
    return HttpResponse("<h2 style='color:green; text-align:center;'>Paiement validé ! Bienvenue chez N'WÉLÉ.</h2>")

@api_view(['GET'])
def profil_chauffeur(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    serializer = ChauffeurSerializer(chauffeur, context={'request': request})
    return Response(serializer.data)