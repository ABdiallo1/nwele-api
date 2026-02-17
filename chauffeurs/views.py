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
def initier_paiement(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        phone = "".join(filter(str.isdigit, str(chauffeur.telephone)))
        payload = {
            "item_name": "Abonnement Taxi N'WÉLÉ",
            "item_price": "100", # Prix de test
            "currency": "XOF",
            "ref_command": f"ABO_{chauffeur.id}_{int(timezone.now().timestamp())}",
            "command_name": f"Paiement chauffeur {chauffeur.nom_complet}",
            "env": "test", # <--- CHANGÉ EN TEST pour éviter l'erreur de production
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
    """ Gère la validation automatique de l'abonnement """
    data = {}
    if request.method == "POST":
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.dict()

    ref = data.get('ref_command')
    # En mode test, PayTech peut envoyer des types d'événements différents
    if ref and "ABO_" in ref:
        try:
            chauffeur_id = ref.split('_')[1]
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            chauffeur.enregistrer_paiement()
            return HttpResponse("OK")
        except Exception:
            pass
    return HttpResponse("Callback Reçu")

# ... (garder les autres fonctions connexion_chauffeur, profil_chauffeur, etc.)