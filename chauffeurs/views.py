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

# --- 1. SETUP ADMIN ---
def creer_admin_force(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@nwele.com', 'Parser1234')
        return HttpResponse("✅ Admin créé avec succès !")
    return HttpResponse("⚠️ L'admin existe déjà.")

# --- 2. CONNEXION DU CHAUFFEUR ---
@api_view(['POST'])
def connexion_chauffeur(request):
    # .strip() nettoie les espaces invisibles qui font souvent échouer la recherche
    telephone = str(request.data.get('telephone', '')).strip()
    print(f"--- Tentative de connexion : [{telephone}] ---")

    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        serializer = ChauffeurSerializer(chauffeur, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Chauffeur.DoesNotExist:
        return Response(
            {"error": "Numéro inconnu. Vérifiez votre saisie ou contactez l'admin."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"🔥 Erreur Connexion: {e}")
        return Response({"error": "Erreur serveur"}, status=500)

# --- 3. PAIEMENT PAYTECH ---
@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    
    PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"
    ref_command = f"PAY-{chauffeur.id}-{int(timezone.now().timestamp())}"
    
    # Utilise tes clés d'environnement Render ou les valeurs par défaut
    api_key = os.getenv("PAYTECH_API_KEY", "VOTRE_CLE")
    api_secret = os.getenv("PAYTECH_API_SECRET", "VOTRE_SECRET")

    payload = {
        "item_name": "Activation Compte N'wele",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": ref_command,
        "command_name": f"Abonnement - {chauffeur.nom_complet}",
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
        response = requests.post(PAYTECH_URL, json=payload, headers=headers, timeout=10)
        res_data = response.json()
        
        if res_data.get('success') == 1:
            return Response({"url": res_data['redirect_url']}, status=200)
        return Response({"error": "Détails PayTech invalides", "details": res_data}, status=400)
    except Exception as e:
        return Response({"error": f"Connexion PayTech échouée: {e}"}, status=500)

# --- 4. CALLBACK (IPN) ---
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
                
                # Appel de la méthode du modèle
                chauffeur.enregistrer_paiement() 
                return Response({"status": "success"}, status=200)
            except Exception as e:
                print(f"❌ Erreur IPN: {e}")
                return Response({"status": "error"}, status=400)
        return Response({"status": "no_ref"}, status=400)

# --- 5. GPS ET LISTE (POUR L'APP CLIENT) ---
@api_view(['PATCH'])
def mettre_a_jour_chauffeur(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    serializer = ChauffeurSerializer(chauffeur, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChauffeurListView(APIView):
    def get(self, request):
        try:
            # On ne montre que ceux qui sont à jour ET qui ont activé le bouton "En ligne"
            chauffeurs = Chauffeur.objects.filter(est_en_ligne=True, est_actif=True)
            serializer = ChauffeurSerializer(chauffeurs, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            print(f"🔥 Erreur Liste: {e}")
            return Response([], status=200) # Renvoie liste vide au lieu de 500

class ChauffeurProfilView(APIView):
    def get(self, request, pk):
        chauffeur = get_object_or_404(Chauffeur, pk=pk)
        serializer = ChauffeurSerializer(chauffeur, context={'request': request})
        return Response(serializer.data)