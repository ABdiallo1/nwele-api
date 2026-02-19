import requests
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur
from .serializers import ChauffeurSerializer

# Configuration FedaPay (Sandbox)
FEDAPAY_API_KEY = "sk_sandbox_JVBu9SjQL5rl3Ka4_muQ0J4h" 
FEDAPAY_URL = "https://api.fedapay.com/v1/transactions"

@csrf_exempt
def connexion_chauffeur(request):
    """ Authentification du chauffeur par numéro de téléphone """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Nettoyage du numéro pour la recherche en base de données
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
    """ Prépare la transaction FedaPay et renvoie l'URL de paiement à Flutter """
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        # Nettoyage strict pour éviter les rejets FedaPay
        tel_propre = "".join(filter(str.isdigit, str(chauffeur.telephone)))
        
        payload = {
            "description": f"Abonnement N'WÉLÉ - {chauffeur.nom_complet}",
            "amount": 100,
            "currency": {"iso": "XOF"},
            "callback_url": f"https://nwele-api.onrender.com/api/profil-chauffeur/{chauffeur.id}/",
            "customer": {
                "firstname": chauffeur.nom_complet,
                "lastname": "Chauffeur",
                "email": f"taxi{chauffeur.id}@nwele.com",
                "phone_number": {"number": tel_propre, "country": "ml"} # ml pour le Mali
            }
        }
        
        headers = {
            "Authorization": f"Bearer {FEDAPAY_API_KEY}", 
            "Content-Type": "application/json"
        }
        
        # 1. Création de la transaction chez FedaPay
        r = requests.post(FEDAPAY_URL, json=payload, headers=headers)
        res_data = r.json()
        
        if r.status_code not in [200, 201]:
            return JsonResponse({"error": "FedaPay Error", "details": res_data}, status=400)
            
        # 2. Extraction sécurisée de l'ID (résout l'erreur 400 sur mobile)
        # On vérifie toutes les structures possibles renvoyées par l'API Sandbox
        transaction = res_data.get('v1/transaction') or res_data.get('transaction') or res_data
        trans_id = transaction.get('id')
        
        if not trans_id:
            return JsonResponse({"error": "ID transaction manquant dans la réponse FedaPay", "debug": res_data}, status=400)
        
        # 3. Génération du Token de paiement
        token_r = requests.post(f"{FEDAPAY_URL}/{trans_id}/token", headers=headers)
        token_data = token_r.json()
        
        # Récupération de l'URL finale de redirection
        url_finale = token_data.get('url') or token_data.get('v1/token', {}).get('url')
        
        return JsonResponse({"url": url_finale})
            
    except Chauffeur.DoesNotExist:
        return JsonResponse({"error": "Chauffeur introuvable"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def fedapay_webhook(request):
    """ Confirmation automatique après paiement réussi via FedaPay """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            if data.get('event') == 'transaction.approved':
                entity = data.get('entity', {})
                # Récupération du numéro utilisé lors du paiement
                phone = entity.get('customer', {}).get('phone_number', {}).get('number')
                
                # On cherche un chauffeur dont le numéro contient ces chiffres
                chauffeur = Chauffeur.objects.filter(telephone__contains=phone).first()
                if chauffeur:
                    chauffeur.enregistrer_paiement()
                    return HttpResponse("OK")
        except Exception: 
            pass
    return HttpResponse("Invalide", status=200)

def profil_chauffeur(request, chauffeur_id):
    """ Renvoie les infos à jour d'un chauffeur (utilisé pour vérifier l'activation) """
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        return JsonResponse(ChauffeurSerializer(chauffeur).data)
    except Exception:
        return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)

@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    """ Mise à jour de la position et du statut en ligne """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            if "latitude" in data: chauffeur.latitude = data["latitude"]
            if "longitude" in data: chauffeur.longitude = data["longitude"]
            if "est_en_ligne" in data: chauffeur.est_en_ligne = data["est_en_ligne"]
            if "plaque_immatriculation" in data: chauffeur.plaque_immatriculation = data["plaque_immatriculation"]
            chauffeur.save()
            return JsonResponse({"status": "success"})
        except Exception:
            return JsonResponse({"error": "Erreur lors de la mise à jour"}, status=400)
    return JsonResponse({"error": "POST requis"}, status=405)

def liste_taxis_actifs(request):
    """ Liste pour l'espace client : uniquement chauffeurs payés ET en ligne """
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    return JsonResponse(ChauffeurSerializer(taxis, many=True).data, safe=False)