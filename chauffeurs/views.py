import json
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur
from .serializers import ChauffeurSerializer

# --- CONFIGURATION PAYTECH ---
PAYTECH_API_KEY = "4708a871b0d511a24050685ff7abfab2e68c69032e1b3d2913647ef46ed656f2"
PAYTECH_API_SECRET = "17cb57b72f679c40ab29eedfcd485bea81582adb770882a78525abfdc57e6784"

@csrf_exempt
def connexion_chauffeur(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            telephone_saisi = str(data.get("telephone", "")).strip()
            
            if not telephone_saisi:
                return JsonResponse({"error": "Numéro requis"}, status=400)

            # Recherche du chauffeur par téléphone
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
            "env": "test", # Change en "live" pour la production
            "ipn_url": "https://nwele-api.onrender.com/api/paytech-callback/",
            "success_url": "https://nwele-api.onrender.com/paiement-reussi/",
            "cancel_url": "https://nwele-api.onrender.com/paiement-annule/",
        }
        headers = {
            "Accept": "application/json", 
            "Content-Type": "application/json",
            "API_KEY": PAYTECH_API_KEY, 
            "API_SECRET": PAYTECH_API_SECRET
        }
        r = requests.post("https://paytech.sn/api/payment/request-payment", json=payload, headers=headers)
        return JsonResponse(r.json())
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def paytech_callback(request):
    """Callback appelé par PayTech après le paiement (IPN)"""
    try:
        ref = request.POST.get('ref_command', "")
        if "ABO_" in ref:
            c_id = ref.replace("ABO_", "")
            chauffeur = Chauffeur.objects.get(id=c_id)
            # Appelle la méthode du modèle pour activer l'abonnement
            chauffeur.enregistrer_paiement()
            return HttpResponse("OK")
    except Exception as e:
        return HttpResponse("Error", status=200)

def profil_chauffeur(request, chauffeur_id):
    """Vérification du statut pour Flutter"""
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        serializer = ChauffeurSerializer(chauffeur)
        return JsonResponse(serializer.data)
    except:
        return JsonResponse({"error": "Inconnu"}, status=404)

@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    """Mise à jour GPS et Statut En Ligne"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            
            # Harmonisation avec les clés envoyées par Flutter
            if "latitude" in data:
                chauffeur.latitude = data.get("latitude")
            if "longitude" in data:
                chauffeur.longitude = data.get("longitude")
            if "est_en_ligne" in data:
                chauffeur.est_en_ligne = data.get("est_en_ligne")
            
            chauffeur.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "POST requis"}, status=405)