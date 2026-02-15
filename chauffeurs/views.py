import json
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur
from .serializers import ChauffeurSerializer
from django.utils import timezone

# --- CONFIGURATION PAYTECH ---
PAYTECH_API_KEY = "4708a871b0d511a24050685ff7abfab2e68c69032e1b3d2913647ef46ed656f2"
PAYTECH_API_SECRET = "17cb57b72f679c40ab29eedfcd485bea81582adb770882a78525abfdc57e6784"

@csrf_exempt
def connexion_chauffeur(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            tel = "".join(filter(str.isdigit, str(data.get("telephone", ""))))
            chauffeur = Chauffeur.objects.filter(telephone=tel).first()
            if chauffeur:
                return JsonResponse(ChauffeurSerializer(chauffeur).data, status=200)
            return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)
        except:
            return JsonResponse({"error": "Erreur format JSON"}, status=400)
    return JsonResponse({"error": "POST requis"}, status=405)

@csrf_exempt
def initier_paiement(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        payload = {
            "item_name": "Abonnement Taxi N'WÉLÉ",
            "item_price": "10000",
            "currency": "XOF",
            "ref_command": f"ABO_{chauffeur.id}_{int(timezone.now().timestamp())}",
            "command_name": f"Paiement chauffeur {chauffeur.nom_complet}",
            "env": "test",
            "ipn_url": "https://nwele-api.onrender.com/api/paytech-callback/",
            "success_url": "https://nwele-api.onrender.com/api/profil-chauffeur/" + str(chauffeur.id),
            "cancel_url": "https://nwele-api.onrender.com/api/profil-chauffeur/" + str(chauffeur.id),
        }
        headers = {
            "Accept": "application/json", "Content-Type": "application/json",
            "API_KEY": PAYTECH_API_KEY, "API_SECRET": PAYTECH_API_SECRET
        }
        r = requests.post("https://paytech.sn/api/payment/request-payment", json=payload, headers=headers)
        return JsonResponse(r.json())
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# --- LA FONCTION QUI MANQUAIT ---
@csrf_exempt
def paytech_callback(request):
    """C'est ici que PayTech confirme le paiement"""
    try:
        # PayTech envoie les données en POST (form-data)
        ref = request.POST.get('ref_command', "")
        if "ABO_" in ref:
            # On extrait l'ID (ex: ABO_5_17000 -> 5)
            c_id = ref.split('_')[1]
            chauffeur = Chauffeur.objects.get(id=c_id)
            chauffeur.enregistrer_paiement()
            return HttpResponse("OK")
    except Exception as e:
        print(f"Erreur Callback: {e}")
    return HttpResponse("Erreur ou Ref Invalide", status=200)

def profil_chauffeur(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        return JsonResponse(ChauffeurSerializer(chauffeur).data)
    except:
        return JsonResponse({"error": "Inconnu"}, status=404)

@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            if "latitude" in data: chauffeur.latitude = data.get("latitude")
            if "longitude" in data: chauffeur.longitude = data.get("longitude")
            if "est_en_ligne" in data: chauffeur.est_en_ligne = data.get("est_en_ligne")
            chauffeur.save()
            return JsonResponse({"status": "success"})
        except:
            return JsonResponse({"error": "Echec mise à jour"}, status=400)
    return JsonResponse({"error": "POST requis"}, status=405)
# Django views.py
def liste_taxis_actifs(request):
    # Filtre : abonnement actif ET switch "en ligne" activé
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    serializer = ChauffeurSerializer(taxis, many=True)
    return JsonResponse(serializer.data, safe=False)