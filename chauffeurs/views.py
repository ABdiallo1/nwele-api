from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
import uuid
import json

from .models import Chauffeur
from .serializers import ChauffeurSerializer

# --- 1. CONNEXION DU CHAUFFEUR ---
@csrf_exempt
@api_view(['POST'])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone')
    if not telephone:
        return Response({"error": "Téléphone requis"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        # On passe le 'request' au serializer pour avoir les URLs complètes des photos
        serializer = ChauffeurSerializer(chauffeur, context={'request': request})
        return Response(serializer.data)
    except Chauffeur.DoesNotExist:
        return Response({"error": "Chauffeur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

# --- 2. INITIALISATION PAIEMENT PAYTECH ---
@csrf_exempt
@api_view(['POST'])
def initier_paiement_paytech(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    url_paytech = "https://paytech.sn/api/payment/request-payment"
    
    payload = {
        "item_name": "Activation Compte N'WÉLÉ",
        "item_price": "100", 
        "currency": "XOF",
        "ref_command": f"REF-{chauffeur.id}-{uuid.uuid4().hex[:6]}",
        "command_name": f"Paiement de {chauffeur.nom_complet}",
        "env": "test", # Change en 'live' plus tard
        "ipn_url": "https://nwele-api.onrender.com/api/paytech-webhook/",
        "success_url": "https://nwele-api.onrender.com/api/paiement-reussi/",
        "cancel_url": "https://nwele-api.onrender.com/api/paiement-annule/"
    }

    headers = {
        "API_KEY": "060d40fb176378946768ec75949d012489063236965be813952f974714f31835",
        "API_SECRET": "358700259e519280145656113824141686415059635e985472251a31d900696a",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url_paytech, json=payload, headers=headers)
        data = response.json()
        if data.get('success') == 1:
            return Response({'url': data['redirect_url']})
        return Response({'error': 'Erreur PayTech'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# --- 3. MISE À JOUR GPS ---
@csrf_exempt
@api_view(['POST'])
def update_chauffeur(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    serializer = ChauffeurSerializer(chauffeur, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 4. LISTE DES TAXIS ACTIFS (POUR LA CARTE) ---
@api_view(['GET'])
def liste_taxis_actifs(request):
    # Un taxi est affiché si : abonnement payé (est_actif) ET switch ON (est_en_ligne)
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    serializer = ChauffeurSerializer(taxis, many=True, context={'request': request})
    return Response(serializer.data)

# --- 5. WEBHOOK & PAGES DE RETOUR ---
@csrf_exempt
def paytech_webhook(request):
    if request.method == 'POST':
        ref_command = request.POST.get('ref_command')
        type_event = request.POST.get('type_event')
        if type_event == 'sale_complete' and ref_command:
            chauffeur_id = ref_command.split('-')[1]
            Chauffeur.objects.filter(id=chauffeur_id).update(est_actif=True)
            return HttpResponse("OK")
    return HttpResponse("Invalid", status=400)

def paiement_reussi(request):
    return HttpResponse("<h2>Paiement réussi ! Retournez dans l'application N'WÉLÉ.</h2>")

@api_view(['GET'])
def profil_chauffeur(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    serializer = ChauffeurSerializer(chauffeur, context={'request': request})
    return Response(serializer.data)