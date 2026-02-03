import os
import requests
from django.shortcuts import get_object_or_404
from django.utils import timezone
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
    return HttpResponse("⚠️ L'admin existe déjà.")

# --- 2. CONNEXION DU CHAUFFEUR ---
@api_view(['POST'])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone', '').strip()
    chauffeur = Chauffeur.objects.filter(telephone=telephone).first()
    
    if chauffeur:
        serializer = ChauffeurSerializer(chauffeur, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response({"error": "Chauffeur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

# --- 3. MISE À JOUR POSITION ET STATUT ---
@api_view(['PATCH'])
def mettre_a_jour_chauffeur(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    
    if not chauffeur.est_actif and request.data.get('est_en_ligne') == True:
        return Response({"error": "Abonnement expiré"}, status=status.HTTP_403_FORBIDDEN)
        
    serializer = ChauffeurSerializer(chauffeur, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 4. LISTE DES CHAUFFEURS (CLIENT) ---
class ChauffeurListView(APIView):
    def get(self, request):
        chauffeurs = Chauffeur.objects.filter(est_en_ligne=True, est_actif=True)
        serializer = ChauffeurSerializer(chauffeurs, many=True, context={'request': request})
        return Response(serializer.data)

# --- 5. PROFIL INDIVIDUEL ---
class ChauffeurProfilView(APIView):
    def get(self, request, pk):
        chauffeur = get_object_or_404(Chauffeur, pk=pk)
        serializer = ChauffeurSerializer(chauffeur, context={'request': request})
        return Response(serializer.data)

# --- 6. DEMANDE DE PAIEMENT PAYTECH ---
@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    
    PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"
    ref_command = f"PAY-{chauffeur.id}-{int(timezone.now().timestamp())}"
    
    api_key = os.getenv("PAYTECH_API_KEY")
    api_secret = os.getenv("PAYTECH_API_SECRET")

    payload = {
        "item_name": "Activation Compte Nwele",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": ref_command,
        "command_name": f"Abonnement 30j - {chauffeur.nom_complet}",
        "env": "test",
        "success_url": "https://nwele-api.onrender.com/admin/",
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
            return Response({"url": res_data['redirect_url']}, status=200)
        
        return Response({"error": "Erreur PayTech", "details": res_data}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# --- 7. CALLBACK (IPN) : ACTIVATION AUTOMATIQUE ---
@method_decorator(csrf_exempt, name='dispatch')
class PaytechCallbackView(APIView):
    def post(self, request):
        data = request.data
        ref_command = data.get('ref_command')
        
        if ref_command:
            try:
                parts = ref_command.split('-')
                chauffeur_id = parts[1]
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                chauffeur.enregistrer_paiement() 
                return Response({"status": "success"}, status=200)
            except Exception as e:
                return Response({"status": "error", "message": str(e)}, status=400)
                
        return Response({"status": "no_ref"}, status=400)