import requests
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Chauffeur
from .serializers import ChauffeurSerializer

# 1. Vue pour lister les chauffeurs (pour Flutter)
class ChauffeurListView(APIView):
    def get(self, request):
        chauffeurs = Chauffeur.objects.filter(est_en_ligne=True)
        serializer = ChauffeurSerializer(chauffeurs, many=True, context={'request': request})
        return Response(serializer.data)

# 2. Vue pour demander un paiement PayTech
class PaiementChauffeurView(APIView):
    def post(self, request, chauffeur_id):
        chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
        
        PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"
        
        # On crée une référence unique pour cette transaction
        ref_command = f"PAY-{chauffeur.id}-{int(timezone.now().timestamp())}"
        
        payload = {
            "item_name": f"Abonnement 30 jours - {chauffeur.nom}",
            "item_price": "5000",
            "currency": "XOF",
            "ref_command": ref_command,
            "command_name": f"Renouvellement Nwele {chauffeur.telephone}",
            "success_url": "https://nwele-api.onrender.com/paiement/succes/",
            "ipn_url": "https://nwele-api.onrender.com/api/paiement/callback/", 
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "API_KEY": "VOTRE_API_KEY", # À remplacer par ta clé PayTech
            "API_SECRET": "VOTRE_API_SECRET" # À remplacer par ta clé PayTech
        }

        try:
            response = requests.post(PAYTECH_URL, json=payload, headers=headers)
            res_data = response.json()
            if res_data.get('success') == 1:
                return Response({
                    "url": res_data['redirect_url'],
                    "ref_command": ref_command
                })
            return Response({"error": "PayTech a refusé la requête"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 3. Le Callback (IPN) : Reçoit la confirmation de PayTech
@method_decorator(csrf_exempt, name='dispatch')
class PaytechCallbackView(APIView):
    def post(self, request):
        # PayTech envoie les données en POST
        data = request.data
        
        # On vérifie si le paiement a réussi
        # PayTech envoie 'type_event': 'sale_complete' ou similaire selon leur doc
        ref_command = data.get('ref_command')
        
        if ref_command:
            try:
                # On extrait l'ID du chauffeur depuis la référence (PAY-ID-TIMESTAMP)
                parts = ref_command.split('-')
                chauffeur_id = parts[1]
                
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                chauffeur.enregistrer_paiement() # Cette méthode active le chauffeur et ajoute 30 jours
                
                print(f"✅ Abonnement activé pour {chauffeur.nom}")
                return Response({"status": "success"}, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"❌ Erreur callback : {e}")
                
        return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)