import os
import requests
import uuid
import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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
    
    # RÉCUPÉRATION DYNAMIQUE DES CLÉS DEPUIS RENDER
    api_key = os.getenv('PAYTECH_API_KEY')
    api_secret = os.getenv('PAYTECH_SECRET_KEY')

    if not api_key or not api_secret:
        return Response({'error': 'Clés API manquantes sur le serveur Render'}, status=500)

    # CORRECTION : Tout ce qui suit doit être indenté (décalé à droite)
    payload = {
        "item_name": "Activation Compte N'WÉLÉ",
        "item_price": "100", 
        "currency": "XOF",
        "ref_command": f"REF-{chauffeur.id}-{uuid.uuid4().hex[:6]}",
        "command_name": f"Paiement de {chauffeur.nom_complet}",
        "env": "prod", # Mode réel accepté par PayTech
        "ipn_url": "https://nwele-api.onrender.com/api/paytech-webhook/",
        "success_url": "https://nwele-api.onrender.com/api/paiement-reussi/",
        "cancel_url": "https://nwele-api.onrender.com/api/paiement-annule/"
    }

    headers = {
        "API_KEY": api_key,
        "API_SECRET": api_secret,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url_paytech, json=payload, headers=headers)
        data = response.json()
        
        print(f"DEBUG PAYTECH: {data}")

        if data.get('success') == 1:
            return Response({'url': data['redirect_url']})
        
        error_msg = data.get('error', ['Erreur PayTech inconnue'])[0]
        return Response({'error': error_msg}, status=400)

    except Exception as e:
        return Response({'error': f"Erreur réseau : {str(e)}"}, status=500)

# --- 3. MISE À JOUR GPS / STATUT ---
@csrf_exempt
@api_view(['POST'])
def update_chauffeur(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    serializer = ChauffeurSerializer(chauffeur, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 4. LISTE DES TAXIS ACTIFS ---
@api_view(['GET'])
def liste_taxis_actifs(request):
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
            try:
                chauffeur_id = ref_command.split('-')[1]
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                chauffeur.est_actif = True
                chauffeur.save()
                return HttpResponse("OK")
            except Exception as e:
                return HttpResponse("Erreur interne", status=500)
                
    return HttpResponse("Invalide", status=400)

def paiement_reussi(request):
    return HttpResponse("""
        <div style='text-align:center; padding-top:50px; font-family:sans-serif;'>
            <h2 style='color:green;'>✅ Paiement réussi !</h2>
            <p>Votre compte N'WÉLÉ est maintenant activé.</p>
            <p>Retournez dans l'application.</p>
        </div>
    """)

@api_view(['GET'])
def profil_chauffeur(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    serializer = ChauffeurSerializer(chauffeur, context={'request': request})
    return Response(serializer.data)