import os, requests, json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur
from .serializers import ChauffeurSerializer

FEDAPAY_API_KEY = os.environ.get('FEDAPAY_API_KEY', 'sk_sandbox_JVBu9SjQL5rl3Ka4_muQ0J4h')
FEDAPAY_URL = "https://api.fedapay.com/v1/transactions"

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
            return JsonResponse({"error": "Erreur données"}, status=400)

@csrf_exempt
def initier_paiement(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        payload = {
            "description": f"Paiement N'WÉLÉ - {chauffeur.nom_complet}",
            "amount": 100,
            "currency": {"iso": "XOF"},
            "customer": {
                "firstname": chauffeur.nom_complet,
                "phone_number": {"number": chauffeur.telephone, "country": "ml"}
            }
        }
        headers = {"Authorization": f"Bearer {FEDAPAY_API_KEY.strip()}"}
        
        r = requests.post(FEDAPAY_URL, json=payload, headers=headers)
        res_data = r.json()
        trans_id = (res_data.get('v1/transaction') or res_data.get('transaction')).get('id')
        
        token_r = requests.post(f"{FEDAPAY_URL}/{trans_id}/token", headers=headers)
        return JsonResponse({"url": token_r.json().get('url')})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    if request.method == "POST":
        data = json.loads(request.body)
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        if "latitude" in data: chauffeur.latitude = data["latitude"]
        if "longitude" in data: chauffeur.longitude = data["longitude"]
        if "est_en_ligne" in data: chauffeur.est_en_ligne = data["est_en_ligne"]
        chauffeur.save()
        return JsonResponse({"status": "success"})

def liste_taxis_actifs(request):
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    return JsonResponse(ChauffeurSerializer(taxis, many=True).data, safe=False)

def profil_chauffeur(request, chauffeur_id):
    chauffeur = Chauffeur.objects.get(id=chauffeur_id)
    return JsonResponse(ChauffeurSerializer(chauffeur).data)