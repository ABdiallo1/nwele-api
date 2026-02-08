import os, requests
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Chauffeur

@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    
    # NETTOYAGE DU TELEPHONE (Enlever les espaces pour éviter l'erreur pho)
    telephone_propre = chauffeur.telephone.replace(" ", "").replace(".", "").replace("-", "")
    
    PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"
    ref_command = f"PAY-{chauffeur.id}-{int(timezone.now().timestamp())}"
    
    api_key = os.getenv("PAYTECH_API_KEY", "TA_CLE_API_ICI")
    api_secret = os.getenv("PAYTECH_API_SECRET", "TON_SECRET_ICI")

    payload = {
        "item_name": "Abonnement N'WELE",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": ref_command,
        "command_name": f"Abonnement - {chauffeur.nom_complet}",
        "env": "test", 
        "customer_phone": telephone_propre, 
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
        response = requests.post(PAYTECH_URL, json=payload, headers=headers, timeout=10)
        res_data = response.json()
        
        # Vérification très précise du succès
        if response.status_code == 200 and res_data.get('success') == 1:
            return Response({"url": res_data['redirect_url']}, status=200)
        else:
            # ICI on voit l'erreur exacte dans les logs Render
            print(f"--- ERREUR PAYTECH ---")
            print(f"Payload envoyé: {payload}")
            print(f"Réponse reçue: {res_data}")
            return Response({
                "error": "PayTech a refusé la requête",
                "details": res_data
            }, status=400)

    except Exception as e:
        print(f"--- ERREUR CRITIQUE --- : {str(e)}")
        return Response({"error": f"Erreur serveur: {str(e)}"}, status=500)