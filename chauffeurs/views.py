import os
import requests
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Chauffeur
from .serializers import ChauffeurSerializer

# Récupération de la clé depuis Render ou valeur par défaut
FEDAPAY_API_KEY = os.environ.get('FEDAPAY_API_KEY', 'sk_sandbox_JVBu9SjQL5rl3Ka4_muQ0J4h')
FEDAPAY_URL = "https://api.fedapay.com/v1/transactions"

@csrf_exempt
def connexion_chauffeur(request):
    """ Authentification par téléphone lors de l'ouverture de l'app """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Nettoyage pour ne garder que les chiffres
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
    """ Prépare la transaction FedaPay pour Flutter """
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        # Nettoyage du téléphone pour éviter les rejets FedaPay
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
                "phone_number": {"number": tel_propre, "country": "ml"}
            }
        }
        
        headers = {
            "Authorization": f"Bearer {FEDAPAY_API_KEY}", 
            "Content-Type": "application/json"
        }
        
        # 1. Création de la transaction
        r = requests.post(FEDAPAY_URL, json=payload, headers=headers)
        
        if r.status_code not in [200, 201]:
            # En cas d'erreur d'authentification, on renvoie les détails FedaPay
            return JsonResponse({"error": "Erreur d'authentification FedaPay", "details": r.json()}, status=r.status_code)
            
        res_data = r.json()
        transaction = res_data.get('v1/transaction') or res_data.get('transaction') or res_data
        trans_id = transaction.get('id')
        
        # 2. Génération du Token de paiement (URL checkout)
        token_r = requests.post(f"{FEDAPAY_URL}/{trans_id}/token", headers=headers)
        token_data = token_r.json()
        
        # Extraction de l'URL pour la WebView Flutter
        url_paiement = token_data.get('url') or token_data.get('v1/token', {}).get('url')
        
        return JsonResponse({"url": url_paiement})
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def fedapay_webhook(request):
    """ Reçoit la confirmation de paiement de FedaPay """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Vérification du succès de la transaction
            if data.get('event') == 'transaction.approved':
                entity = data.get('entity', {})
                phone = entity.get('customer', {}).get('phone_number', {}).get('number')
                
                # Activation du chauffeur correspondant
                chauffeur = Chauffeur.objects.filter(telephone__contains=phone).first()
                if chauffeur:
                    chauffeur.enregistrer_paiement()
                    return HttpResponse("OK")
        except Exception:
            pass
    return HttpResponse("Invalide", status=200)

def profil_chauffeur(request, chauffeur_id):
    """ Retourne les données à jour (pour vérifier si est_actif est passé à True) """
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        return JsonResponse(ChauffeurSerializer(chauffeur).data)
    except Exception:
        return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)

@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    """ Mise à jour GPS et statut en ligne """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            if "latitude" in data: chauffeur.latitude = data["latitude"]
            if "longitude" in data: chauffeur.longitude = data["longitude"]
            if "est_en_ligne" in data: chauffeur.est_en_ligne = data["est_en_ligne"]
            chauffeur.save()
            return JsonResponse({"status": "success"})
        except Exception:
            return JsonResponse({"error": "Erreur mise à jour"}, status=400)
    return JsonResponse({"error": "POST requis"}, status=405)

def liste_taxis_actifs(request):
    """ Pour les clients : voir les taxis qui ont payé ET sont en ligne """
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    return JsonResponse(ChauffeurSerializer(taxis, many=True).data, safe=False)