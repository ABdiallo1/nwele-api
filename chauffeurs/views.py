import json
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Chauffeur
from .serializers import ChauffeurSerializer

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
                return JsonResponse(ChauffeurSerializer(chauffeur).data)
            return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)
        except:
            return JsonResponse({"error": "Données invalides"}, status=400)
    return JsonResponse({"error": "POST requis"}, status=405)

@csrf_exempt
def initier_paiement(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        phone = "".join(filter(str.isdigit, str(chauffeur.telephone)))
        payload = {
            "item_name": "Abonnement Taxi N'WÉLÉ",
            "item_price": "100", 
            "currency": "XOF",
            "ref_command": f"ABO_{chauffeur.id}_{int(timezone.now().timestamp())}",
            "command_name": f"Paiement chauffeur {chauffeur.nom_complet}",
            "env": "prod", 
            "ipn_url": "https://nwele-api.onrender.com/api/paytech-callback/",
            "success_url": f"https://nwele-api.onrender.com/api/profil-chauffeur/{chauffeur.id}/",
            "cancel_url": f"https://nwele-api.onrender.com/api/profil-chauffeur/{chauffeur.id}/",
            "customer_phone": phone,
        }
        headers = {"API_KEY": PAYTECH_API_KEY, "API_SECRET": PAYTECH_API_SECRET}
        r = requests.post("https://paytech.sn/api/payment/request-payment", json=payload, headers=headers)
        return JsonResponse(r.json())
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def paytech_callback(request):
    ref = request.POST.get('ref_command')
    if not ref and request.body:
        try:
            ref = json.loads(request.body).get('ref_command')
        except: pass
    if ref and "ABO_" in ref:
        try:
            chauffeur_id = ref.split('_')[1]
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            chauffeur.enregistrer_paiement()
            return HttpResponse("OK")
        except: pass
    return HttpResponse("Invalide", status=200)

def profil_chauffeur(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        return JsonResponse(ChauffeurSerializer(chauffeur).data)
    except:
        return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)

@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            if "latitude" in data: chauffeur.latitude = data["latitude"]
            if "longitude" in data: chauffeur.longitude = data["longitude"]
            if "est_en_ligne" in data: chauffeur.est_en_ligne = data["est_en_ligne"]
            chauffeur.save()
            return JsonResponse({"status": "success"})
        except:
            return JsonResponse({"error": "Erreur mise à jour"}, status=400)
    return JsonResponse({"error": "POST requis"}, status=405)

def liste_taxis_actifs(request):
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    return JsonResponse(ChauffeurSerializer(taxis, many=True).data, safe=False)