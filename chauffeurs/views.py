import os
import requests
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone  # Ajouté : nécessaire pour ref_command
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .models import Chauffeur
from .serializers import ChauffeurSerializer

# --- 1. SÉCURITÉ : CRÉATION FORCE DE L'ADMIN ---
def creer_admin_force(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@nwele.com', 'Parser1234')
        return HttpResponse("✅ Admin créé avec succès ! Connectez-vous sur /admin/")
    return HttpResponse("⚠️ L'admin existe déjà. Utilisez 'admin' et 'Parser1234'")

# --- 2. LISTE DES CHAUFFEURS POUR LA CARTE ---
class ChauffeurListView(APIView):
    def get(self, request):
        # On ne montre que les chauffeurs actifs et en ligne
        chauffeurs = Chauffeur.objects.filter(est_en_ligne=True, est_actif=True)
        serializer = ChauffeurSerializer(chauffeurs, many=True, context={'request': request})
        return Response(serializer.data)

# --- 3. PROFIL INDIVIDUEL ---
class ChauffeurProfilView(APIView):
    def get(self, request, pk):
        chauffeur = get_object_or_404(Chauffeur, pk=pk)
        serializer = ChauffeurSerializer(chauffeur, context={'request': request})
        return Response(serializer.data)

# --- 4. DEMANDE DE PAIEMENT PAYTECH ---
@api_view(['GET', 'POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    
    PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"
    # Création d'une référence unique pour le paiement
    ref_command = f"PAY-{chauffeur.id}-{int(timezone.now().timestamp())}"
    
    # Récupération des clés API configurées sur Render
    api_key = os.getenv("PAYTECH_API_KEY")
    api_secret = os.getenv("PAYTECH_API_SECRET")

    payload = {
        "item_name": "Frais d'activation Compte Chauffeur Nwele",
        "item_price": "10000", # Le chauffeur paie 10 000 FCFA
        "currency": "XOF",
        "ref_command": ref_command,
        "command_name": f"Abonnement 30j - {chauffeur.nom_complet}",
        "env": "test", # Reste en 'test' pour tes essais
        "success_url": "https://nwele-api.onrender.com/admin/chauffeurs/chauffeur/",
        "ipn_url": "https://nwele-api.onrender.com/api/paiement/callback/", 
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "API_KEY": api_key,
        "API_SECRET": api_secret
    }

    try:
        response = requests.post(PAYTECH_URL, json=payload, headers=headers)
        res_data = response.json()
        
        if res_data.get('success') == 1:
            # Redirection automatique vers Orange Money/Wave/Free
            return redirect(res_data['redirect_url'])
        
        return Response({"error": "Erreur PayTech", "details": res_data}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# --- 5. CALLBACK (IPN) : ACTIVATION AUTOMATIQUE DU CHAUFFEUR ---
@method_decorator(csrf_exempt, name='dispatch')
class PaytechCallbackView(APIView):
    def post(self, request):
        # PayTech envoie les données de confirmation ici après le paiement
        data = request.data
        ref_command = data.get('ref_command')
        
        if ref_command:
            try:
                # On extrait l'ID du chauffeur depuis la référence (PAY-ID-TIMESTAMP)
                parts = ref_command.split('-')
                chauffeur_id = parts[1]
                
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                # Cette méthode active 'est_actif' et ajoute 30 jours (déjà dans ton model)
                chauffeur.enregistrer_paiement() 
                
                return Response({"status": "success"}, status=200)
            except Exception as e:
                return Response({"status": "error", "message": str(e)}, status=400)
                
        return Response({"status": "no_ref"}, status=400)