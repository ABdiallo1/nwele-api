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

from .models import Chauffeur
from .serializers import ChauffeurSerializer

# --- 1. SÉCURITÉ : CRÉATION FORCE DE L'ADMIN ---
# Visitez https://nwele-api.onrender.com/api/setup-admin/ si l'admin ne marche pas
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

# --- 3. PROFIL INDIVIDUEL (POUR VÉRIFIER LE STATUT) ---
class ChauffeurProfilView(APIView):
    def get(self, request, pk):
        chauffeur = get_object_or_404(Chauffeur, pk=pk)
        serializer = ChauffeurSerializer(chauffeur, context={'request': request})
        return Response(serializer.data)

# --- 4. DEMANDE DE PAIEMENT PAYTECH ---
class PaiementChauffeurView(APIView):
    def post(self, request, chauffeur_id):
        chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
        
        PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"
        ref_command = f"PAY-{chauffeur.id}-{int(timezone.now().timestamp())}"
        
        payload = {
            "item_name": f"Abonnement 30 jours - {chauffeur.nom}",
            "item_price": "10000",
            "currency": "XOF",
            "ref_command": ref_command,
            "command_name": f"Abonnement Nwele {chauffeur.telephone}",
            "success_url": "https://nwele-api.onrender.com/api/paiement/succes/",
            "ipn_url": "https://nwele-api.onrender.com/api/paiement/callback/", 
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "API_KEY": "VOTRE_API_KEY",    # REMPLACE PAR TA CLÉ
            "API_SECRET": "VOTRE_API_SECRET" # REMPLACE PAR TA CLÉ
        }

        try:
            response = requests.post(PAYTECH_URL, json=payload, headers=headers)
            res_data = response.json()
            if res_data.get('success') == 1:
                return Response({
                    "url": res_data['redirect_url'],
                    "ref_command": ref_command
                })
            return Response({"error": "PayTech a refusé la requête"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

# --- 5. CALLBACK (IPN) : ACTIVATION AUTOMATIQUE ---
@method_decorator(csrf_exempt, name='dispatch')
class PaytechCallbackView(APIView):
    def post(self, request):
        data = request.data
        ref_command = data.get('ref_command')
        
        if ref_command:
            try:
                # Extraction de l'ID : PAY-ID-TIMESTAMP
                parts = ref_command.split('-')
                chauffeur_id = parts[1]
                
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                # Utilise la méthode du modèle pour activer et ajouter 30 jours
                chauffeur.enregistrer_paiement() 
                
                return Response({"status": "success"}, status=200)
            except Exception as e:
                return Response({"status": "error", "message": str(e)}, status=400)
                
        return Response({"status": "no_ref"}, status=400)