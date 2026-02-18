import requests
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur
from .serializers import ChauffeurSerializer

# Tes clés
FEDAPAY_API_KEY = "sk_sandbox_JVBu9SjQL5rl3Ka4_muQ0J4h" 
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
        except Exception:
            return JsonResponse({"error": "Données invalides"}, status=400)
    return JsonResponse({"error": "POST requis"}, status=405)

@csrf_exempt
def initier_paiement(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        # Nettoyage strict du numéro (FedaPay rejette si format invalide)
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
                "phone_number": {"number": tel_propre, "country": "ml"} # ml pour Mali
            }
        }
        
        headers = {
            "Authorization": f"Bearer {FEDAPAY_API_KEY}", 
            "Content-Type": "application/json"
        }
        
        # 1. Création de la transaction
        r = requests.post(FEDAPAY_URL, json=payload, headers=headers)
        res_data = r.json()
        
        if r.status_code not in [200, 201]:
            return JsonResponse({"error": "FedaPay Create Error", "details": res_data}, status=400)
            
        # --- CORRECTION ICI ---
        # FedaPay Sandbox peut renvoyer la transaction directement ou dans une clé 'v1/transaction'
        transaction = res_data.get('v1/transaction') or res_data.get('transaction') or res_data
        trans_id = transaction.get('id')
        
        if not trans_id:
             return JsonResponse({"error": "ID Transaction manquant", "res": res_data}, status=400)

        # 2. Génération du Token/URL de paiement
        token_url = f"{FEDAPAY_URL}/{trans_id}/token"
        token_r = requests.post(token_url, headers=headers)
        token_data = token_r.json()
        
        if token_r.status_code not in [200, 201]:
            return JsonResponse({"error": "FedaPay Token Error", "details": token_data}, status=400)

        # On renvoie l'URL à Flutter
        # Le token data contient une clé 'url' ou 'v1/token' -> 'url'
        final_url = token_data.get('url') or token_data.get('v1/token', {}).get('url')
        
        return JsonResponse({"url": final_url})
            
    except Chauffeur.DoesNotExist:
        return JsonResponse({"error": "Chauffeur introuvable"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def fedapay_webhook(request):
    """ Gère la confirmation automatique du paiement """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Vérification de l'événement FedaPay
            if data.get('event') == 'transaction.approved':
                entity = data.get('entity', {})
                phone_data = entity.get('customer', {}).get('phone_number', {})
                phone = phone_data.get('number')
                
                chauffeur = Chauffeur.objects.filter(telephone__contains=phone).first()
                if chauffeur:
                    chauffeur.enregistrer_paiement()
                    return HttpResponse("OK")
        except Exception: 
            pass
    return HttpResponse("Invalide", status=200)

# Les autres vues (profil_chauffeur, update_chauffeur, liste_taxis_actifs) restent identiques
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
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    return JsonResponse(ChauffeurSerializer(taxis, many=True).data, safe=False)