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
        except Exception:
            return JsonResponse({"error": "Données invalides"}, status=400)
    return JsonResponse({"error": "POST requis"}, status=405)

@csrf_exempt
def initier_paiement(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        phone = "".join(filter(str.isdigit, str(chauffeur.telephone)))
        payload = {
            "item_name": "Abonnement Taxi N'WÉLÉ",
            "item_price": "10000", # Ajusté à 10.000 XOF selon ton image
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
    """ Gère la notification de paiement de PayTech """
    data = {}
    if request.method == "POST":
        # PayTech envoie parfois en POST classique ou en JSON
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.dict()

    ref = data.get('ref_command')
    type_event = data.get('type_event') # Important pour vérifier le succès

    if ref and "ABO_" in ref and type_event == "sale_complete":
        try:
            chauffeur_id = ref.split('_')[1]
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            chauffeur.enregistrer_paiement()
            return HttpResponse("OK")
        except Exception:
            pass
    return HttpResponse("Invalide ou Échoué", status=200)

def profil_chauffeur(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        return JsonResponse(ChauffeurSerializer(chauffeur).data)
    except Exception:
        return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)

@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            # Mise à jour des champs autorisés
            if "latitude" in data: chauffeur.latitude = data["latitude"]
            if "longitude" in data: chauffeur.longitude = data["longitude"]
            if "est_en_ligne" in data: chauffeur.est_en_ligne = data["est_en_ligne"]
            if "plaque_immatriculation" in data: chauffeur.plaque_immatriculation = data["plaque_immatriculation"]
            
            chauffeur.save()
            return JsonResponse({"status": "success", "data": ChauffeurSerializer(chauffeur).data})
        except Exception:
            return JsonResponse({"error": "Erreur mise à jour"}, status=400)
    return JsonResponse({"error": "POST requis"}, status=405)

def liste_taxis_actifs(request):
    # On ne montre que ceux qui ont payé ET qui sont en ligne
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    serializer = ChauffeurSerializer(taxis, many=True)
    return JsonResponse(serializer.data, safe=False)