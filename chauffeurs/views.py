import os, requests
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Chauffeur

@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    
    PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"
    # Génération d'une référence unique
    ref_command = f"PAY-{chauffeur.id}-{int(timezone.now().timestamp())}"
    
    # Récupération des clés (Assure-toi qu'elles sont dans tes variables Render)
    api_key = os.getenv("PAYTECH_API_KEY", "VOTRE_CLE_REELLE")
    api_secret = os.getenv("PAYTECH_API_SECRET", "VOTRE_SECRET_REEL")

    payload = {
        "item_name": "Activation Compte N'wele",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": ref_command,
        "command_name": f"Abonnement - {chauffeur.nom_complet}",
        "env": "test", # Mets 'prod' pour les vrais paiements
        "success_url": "nwele://success", 
        "ipn_url": "https://nwele-api.onrender.com/api/paiement/callback/",
        "custom_field": str(chauffeur.id) # Sécurité pour retrouver le chauffeur à l'IPN
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "API_KEY": api_key,
        "API_SECRET": api_secret
    }

    try:
        response = requests.post(PAYTECH_URL, json=payload, headers=headers, timeout=10)
        res_data = response.json()
        
        if res_data.get('success') == 1:
            return Response({"url": res_data['redirect_url']}, status=200)
        else:
            # Envoie le détail de l'erreur PayTech au log pour voir le code (pho)
            print(f"❌ Erreur PayTech: {res_data}")
            return Response({"error": "PayTech Refusé", "details": res_data}, status=400)
    except Exception as e:
        return Response({"error": f"Erreur serveur: {str(e)}"}, status=500)