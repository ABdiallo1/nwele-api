import os
import requests
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .models import Chauffeur
from .serializers import ChauffeurSerializer

# --- 1. SETUP ADMIN ---
def creer_admin_force(request):
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@nwele.com', 'Parser1234')
        return HttpResponse("✅ Admin créé avec succès !")
    return HttpResponse("⚠️ L'admin existe déjà.")

# --- 2. CONNEXION ---
@api_view(['POST'])
def connexion_chauffeur(request):
    telephone = str(request.data.get('telephone', '')).strip()
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        # On force la vérification de l'expiration à chaque connexion
        _ = chauffeur.jours_restants 
        serializer = ChauffeurSerializer(chauffeur, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Chauffeur.DoesNotExist:
        return Response({"error": "Numéro inconnu."}, status=status.HTTP_404_NOT_FOUND)

# --- 3. PAIEMENT ---
# --- PAIEMENT PAYTECH ---
@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    
    PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"
    ref_command = f"PAY-{chauffeur.id}-{int(timezone.now().timestamp())}"
    
    # REMPLACE BIEN PAR TES VRAIES CLES ICI OU DANS RENDER
    api_key = os.getenv("PAYTECH_API_KEY", "VOTRE_CLE_REELLE")
    api_secret = os.getenv("PAYTECH_API_SECRET", "VOTRE_SECRET_REEL")

    payload = {
        "item_name": "Abonnement N'wele",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": ref_command,
        "command_name": f"Abonnement - {chauffeur.nom_complet}",
        "env": "test", # Change en 'prod' une fois que ça marche
        "success_url": "nwele://success", 
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
        
        if res_data.get('success') == 1:
            return Response({"url": res_data['redirect_url']}, status=200)
        # Si erreur, on renvoie le détail pour debugger
        return Response({"error": "Erreur PayTech", "details": res_data}, status=400)
    except Exception as e:
        return Response({"error": f"Connexion échouée: {e}"}, status=500)

# --- 4. CALLBACK (L'IPN qui valide le paiement) ---
@method_decorator(csrf_exempt, name='dispatch')
class PaytechCallbackView(APIView):
    def post(self, request):
        # PayTech peut envoyer en JSON ou Form-Data
        data = request.data
        ref_command = data.get('ref_command')
        
        print(f"📩 IPN Reçu : {ref_command}") # Pour tes logs sur Render

        if ref_command:
            try:
                # Format attendu : PAY-ID-TIMESTAMP
                parts = ref_command.split('-')
                chauff_id = parts[1]
                chauffeur = Chauffeur.objects.get(id=chauff_id)
                chauffeur.enregistrer_paiement()
                return Response({"status": "OK"}, status=200)
            except Exception as e:
                return Response({"status": "Error", "message": str(e)}, status=400)
        return Response({"status": "No ref"}, status=400)

# --- 5. GPS ET PROFILS ---
@api_view(['PATCH'])
def mettre_a_jour_chauffeur(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    serializer = ChauffeurSerializer(chauffeur, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

class ChauffeurProfilView(APIView):
    def get(self, request, pk):
        chauffeur = get_object_or_404(Chauffeur, pk=pk)
        # On vérifie l'expiration ici aussi pour être sûr que le statut est à jour
        _ = chauffeur.jours_restants
        serializer = ChauffeurSerializer(chauffeur, context={'request': request})
        return Response(serializer.data)

class ChauffeurListView(APIView):
    def get(self, request):
        chauffeurs = Chauffeur.objects.filter(est_en_ligne=True, est_actif=True)
        serializer = ChauffeurSerializer(chauffeurs, many=True, context={'request': request})
        return Response(serializer.data)