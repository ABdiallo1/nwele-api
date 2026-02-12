import os, requests, json
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import Chauffeur
from django.http import HttpResponse
from django.contrib.auth.models import User

@api_view(['POST'])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone', '').replace(" ", "")
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        return Response({
            "id": chauffeur.id,
            "nom_complet": chauffeur.nom_complet,
            "telephone": chauffeur.telephone,
            "est_actif": chauffeur.est_actif,
            "date_expiration": chauffeur.date_expiration.isoformat() if chauffeur.date_expiration else None
        }, status=200)
    except Chauffeur.DoesNotExist:
        return Response({"error": "Chauffeur non trouvé"}, status=404)

@api_view(['POST', 'PATCH'])
def mettre_a_jour_chauffeur(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    data = request.data
    
    # Mise à jour de la position et du statut en ligne
    if 'latitude' in data: chauffeur.latitude = data['latitude']
    if 'longitude' in data: chauffeur.longitude = data['longitude']
    if 'est_en_ligne' in data: chauffeur.est_en_ligne = data['est_en_ligne']
    
    chauffeur.save()
    return Response({"status": "Success", "est_en_ligne": chauffeur.est_en_ligne})

@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    num_propre = "".join(filter(str.isdigit, str(chauffeur.telephone)))
    
    PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"
    ref_command = f"PAY-{chauffeur.id}-{int(timezone.now().timestamp())}"
    
    api_key = os.getenv("PAYTECH_API_KEY", "VOTRE_CLE")
    api_secret = os.getenv("PAYTECH_API_SECRET", "VOTRE_SECRET")

    payload = {
        "item_name": "Abonnement N'WELE",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": ref_command,
        "command_name": f"Paiement {chauffeur.nom_complet}",
        "env": "test", 
        "customer_phone": num_propre,
        "success_url": "https://nwele-api.onrender.com/success/",
        "ipn_url": "https://nwele-api.onrender.com/api/paiement/callback/",
    }
    
    headers = {"Content-Type": "application/json", "API_KEY": api_key, "API_SECRET": api_secret}

    try:
        response = requests.post(PAYTECH_URL, json=payload, headers=headers, timeout=15)
        res_data = response.json()
        if res_data.get('success') == 1:
            return Response({"url": res_data['redirect_url']}, status=200)
        return Response({"error": "Erreur PayTech", "details": res_data}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

class PaytechCallbackView(APIView):
    def post(self, request):
        # PayTech envoie la ref_command (ex: PAY-5-1739...)
        ref_command = request.data.get('ref_command')
        if ref_command:
            try:
                # Extraire l'ID du chauffeur depuis la référence
                chauffeur_id = ref_command.split('-')[1]
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                
                # Activer le chauffeur pour 30 jours
                chauffeur.est_actif = True
                chauffeur.date_expiration = timezone.now() + timedelta(days=30)
                chauffeur.save()
                return Response({"status": "Abonnement activé"}, status=200)
            except Exception as e:
                return Response({"error": str(e)}, status=400)
        return Response({"error": "Référence manquante"}, status=400)

class ChauffeurProfilView(APIView):
    def get(self, request, pk):
        chauffeur = get_object_or_404(Chauffeur, pk=pk)
        return Response({
            "id": chauffeur.id,
            "nom_complet": chauffeur.nom_complet,
            "est_actif": chauffeur.est_actif,
            "est_en_ligne": chauffeur.est_en_ligne,
            "date_expiration": chauffeur.date_expiration
        })

def creer_admin_force(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@nwele.com', 'Parser1234')
        return HttpResponse("✅ Admin créé !")
    return HttpResponse("ℹ️ Déjà existant.")

class ChauffeurListView(APIView):
    def get(self, request):
        # Utile pour la carte côté client
        chauffeurs = Chauffeur.objects.filter(est_en_ligne=True, est_actif=True)
        data = [{"id": c.id, "nom": c.nom_complet, "lat": c.latitude, "lng": c.longitude} for c in chauffeurs]
        return Response(data)