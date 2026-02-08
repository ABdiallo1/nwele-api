import os
import requests
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Chauffeur

@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    # 1. Récupération du chauffeur
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    
    # 2. Nettoyage du numéro (PayTech refuse tout sauf les chiffres)
    num_propre = "".join(filter(str.isdigit, str(chauffeur.telephone)))
    
    # 3. Configuration PayTech
    PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"
    ref_command = f"PAY-{chauffeur.id}-{int(timezone.now().timestamp())}"
    
    # Récupération sécurisée des clés depuis Render
    api_key = os.getenv("PAYTECH_API_KEY", "VOTRE_CLE_REELLE")
    api_secret = os.getenv("PAYTECH_API_SECRET", "VOTRE_SECRET_REEL")

    payload = {
        "item_name": "Abonnement Taxi N'WELE",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": ref_command,
        "command_name": f"Paiement Chauffeur: {chauffeur.nom_complet}",
        "env": "test", # Changez en 'prod' quand tout sera ok
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
        print(f"Tentative de paiement pour {num_propre}...")
        response = requests.post(PAYTECH_URL, json=payload, headers=headers, timeout=15)
        res_data = response.json()
        
        if response.status_code == 200 and res_data.get('success') == 1:
            return Response({"url": res_data['redirect_url']}, status=200)
        else:
            print(f"Erreur PayTech : {res_data}")
            return Response({
                "error": "Le service de paiement a refusé la requête",
                "details": res_data
            }, status=400)
            
    except Exception as e:
        print(f"Erreur Serveur : {str(e)}")
        return Response({"error": "Erreur interne lors de l'appel PayTech"}, status=500)