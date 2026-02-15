import json
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
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
            tel = "".join(filter(str.isdigit, str(data.get("telephone", ""))))
            chauffeur = Chauffeur.objects.filter(telephone=tel).first()
            if chauffeur:
                return JsonResponse(ChauffeurSerializer(chauffeur).data, status=200)
            return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)
        except Exception:
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
            "env": "test",  # Change en 'prod' quand tu seras prêt
            "ipn_url": "https://nwele-api.onrender.com/api/paytech-callback/",
            "success_url": f"https://nwele-api.onrender.com/api/profil-chauffeur/{chauffeur.id}/",
            "cancel_url": f"https://nwele-api.onrender.com/api/profil-chauffeur/{chauffeur.id}/",
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
    """
    Cette fonction reçoit la notification de succès de PayTech (IPN).
    """
    try:
        # PayTech envoie les données en POST
        ref = request.POST.get('ref_command')
        
        # Si vide, on tente de lire le JSON (cas rare chez PayTech mais plus sûr)
        if not ref:
            try:
                data = json.loads(request.body)
                ref = data.get('ref_command')
            except:
                pass

        if ref and "ABO_" in ref:
            c_id = ref.split('_')[1]
            chauffeur = Chauffeur.objects.get(id=c_id)
            
            # Mise à jour du statut du chauffeur
            chauffeur.enregistrer_paiement() 
            
            print(f"Paiement validé pour le chauffeur ID: {c_id}")
            return HttpResponse("OK", status=200)
            
    except Exception as e:
        print(f"Erreur Callback: {str(e)}")
        return HttpResponse(f"Erreur: {str(e)}", status=500)
        
    return HttpResponse("Référence invalide", status=400)

def profil_chauffeur(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        return JsonResponse(ChauffeurSerializer(chauffeur).data)
    except Exception:
        return JsonResponse({"error": "Chauffeur inconnu"}, status=404)

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
        except Exception:
            return JsonResponse({"error": "Echec mise à jour"}, status=400)
    return JsonResponse({"error": "POST requis"}, status=405)

def liste_taxis_actifs(request):
    # On affiche les chauffeurs qui ont payé (est_actif) ET qui sont en ligne
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    serializer = ChauffeurSerializer(taxis, many=True)
    return JsonResponse(serializer.data, safe=False)