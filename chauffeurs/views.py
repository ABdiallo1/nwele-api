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
        return HttpResponse("✅ Admin créé avec succès !")
    return HttpResponse("⚠️ L'admin existe déjà.")

# --- 2. CONNEXION DU CHAUFFEUR ---
@api_view(['POST'])
def connexion_chauffeur(request):
    # .strip() est crucial pour éviter les erreurs d'espaces invisibles
    telephone = str(request.data.get('telephone', '')).strip()
    print(f"--- Tentative de connexion pour : [{telephone}] ---")

    try:
        # Recherche exacte du chauffeur
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        print(f"✅ Chauffeur trouvé : {chauffeur.nom_complet}")
        
        serializer = ChauffeurSerializer(chauffeur, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Chauffeur.DoesNotExist:
        print(f"❌ Erreur : Aucun chauffeur trouvé avec le numéro [{telephone}]")
        # On renvoie un message clair pour Flutter
        return Response(
            {"error": "Numéro inconnu. Veuillez vérifier votre saisie ou contacter l'administrateur."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"⚠️ Erreur serveur lors de la connexion : {str(e)}")
        return Response(
            {"error": "Erreur interne du serveur"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# --- 3. DEMANDE DE PAIEMENT PAYTECH ---
@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    
    PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"
    ref_command = f"PAY-{chauffeur.id}-{int(timezone.now().timestamp())}"
    
    # Récupération des clés API (doivent être configurées dans Render Environment)
    api_key = os.getenv("PAYTECH_API_KEY", "VOTRE_CLE_PAR_DEFAUT")
    api_secret = os.getenv("PAYTECH_API_SECRET", "VOTRE_SECRET_PAR_DEFAUT")

    payload = {
        "item_name": "Activation Compte Nwele",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": ref_command,
        "command_name": f"Abonnement 30j - {chauffeur.nom_complet}",
        "env": "test", # Changez en 'prod' lors du passage au paiement réel
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
        response = requests.post(PAYTECH_URL, json=payload, headers=headers, timeout=10)
        res_data = response.json()
        
        if res_data.get('success') == 1:
            return Response({"url": res_data['redirect_url']}, status=200)
        else:
            return Response({"error": "Erreur PayTech", "details": res_data}, status=400)
            
    except Exception as e:
        return Response({"error": f"Problème de connexion à PayTech : {str(e)}"}, status=500)

# --- 4. CALLBACK (IPN) : ACTIVATION AUTOMATIQUE ---
@method_decorator(csrf_exempt, name='dispatch')
class PaytechCallbackView(APIView):
    def post(self, request):
        # Paytech envoie parfois des données via POST classique ou JSON
        data = request.data
        ref_command = data.get('ref_command')
        
        print(f"--- Réception IPN PayTech : {ref_command} ---")
        
        if ref_command:
            try:
                # Format attendu : PAY-ID-TIMESTAMP
                parts = ref_command.split('-')
                chauffeur_id = parts[1]
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                
                # Active l'abonnement
                chauffeur.enregistrer_paiement() 
                print(f"💰 Paiement confirmé pour {chauffeur.nom_complet}")
                return Response({"status": "success"}, status=200)
            except Exception as e:
                print(f"❌ Erreur IPN : {str(e)}")
                return Response({"status": "error", "message": str(e)}, status=400)
                
        return Response({"status": "no_ref"}, status=400)

# --- 5. AUTRES VUES (GPS ET LISTE) ---
@api_view(['PATCH'])
def mettre_a_jour_chauffeur(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    serializer = ChauffeurSerializer(chauffeur, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

class ChauffeurListView(APIView):
    def get(self, request):
        # Liste pour les clients : uniquement actifs et en ligne
        chauffeurs = Chauffeur.objects.filter(est_en_ligne=True, est_actif=True)
        serializer = ChauffeurSerializer(chauffeurs, many=True, context={'request': request})
        return Response(serializer.data)

class ChauffeurProfilView(APIView):
    def get(self, request, pk):
        chauffeur = get_object_or_404(Chauffeur, pk=pk)
        serializer = ChauffeurSerializer(chauffeur, context={'request': request})
        return Response(serializer.data)