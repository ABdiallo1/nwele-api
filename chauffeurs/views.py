import json
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur
from .serializers import ChauffeurSerializer

# --- CONFIGURATION PAYTECH ---
PAYTECH_API_KEY = "TA_CLE_API" # Mets ta vraie clé
PAYTECH_API_SECRET = "TON_SECRET_API" # Mets ton vrai secret

@csrf_exempt
def connexion_chauffeur(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            telephone_saisi = str(data.get("telephone", "")).strip()
            
            if not telephone_saisi:
                return JsonResponse({"error": "Numéro requis"}, status=400)

            # Recherche du chauffeur
            chauffeur = Chauffeur.objects.filter(telephone=telephone_saisi).first()
            
            if chauffeur:
                serializer = ChauffeurSerializer(chauffeur)
                return JsonResponse(serializer.data, status=200)
            
            return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

@csrf_exempt
def initier_paiement(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        payload = {
            "item_name": "Abonnement N'WÉLÉ",
            "item_price": "10000",
            "currency": "XOF",
            "ref_command": f"ABO_{chauffeur.id}",
            "command_name": f"Abonnement de {chauffeur.nom_complet}",
            "env": "test",
            "ipn_url": "https://nwele-api.onrender.com/api/paytech-callback/",
            "success_url": "https://nwele-api.onrender.com/paiement-reussi/",
            "cancel_url": "https://nwele-api.onrender.com/paiement-annule/",
            "custom_field": json.dumps({"chauffeur_id": chauffeur.id})
        }
        headers = {
            "Accept": "application/json", "Content-Type": "application/json",
            "API_KEY": PAYTECH_API_KEY, "API_SECRET": PAYTECH_API_SECRET
        }
        r = requests.post("https://paytech.sn/api/payment/request-payment", json=payload, headers=headers)
        return JsonResponse(r.json())
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def paytech_callback(request):
    try:
        # PayTech envoie souvent ref_command pour identifier la vente
        ref = request.POST.get('ref_command', "")
        if "ABO_" in ref:
            c_id = ref.replace("ABO_", "")
            chauffeur = Chauffeur.objects.get(id=c_id)
            # On utilise la fonction de ton modèle pour activer l'abonnement
            chauffeur.enregistrer_paiement()
            return HttpResponse("OK")
    except Exception as e:
        return HttpResponse("Error", status=200)

def profil_chauffeur(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        serializer = ChauffeurSerializer(chauffeur)
        return JsonResponse(serializer.data)
    except:
        return JsonResponse({"error": "Inconnu"}, status=404)

@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            chauffeur.latitude = data.get("lat", chauffeur.latitude)
            chauffeur.longitude = data.get("lng", chauffeur.longitude)
            chauffeur.est_en_ligne = data.get("est_en_ligne", False)
            chauffeur.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)