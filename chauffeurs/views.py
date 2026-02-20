import os
import requests
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur
from .serializers import ChauffeurSerializer

# 1. Configuration FedaPay (Lecture depuis les variables d'environnement de Render)
FEDAPAY_API_KEY = os.environ.get('FEDAPAY_API_KEY', 'sk_sandbox_JVBu9SjQL5rl3Ka4_muQ0J4h')
FEDAPAY_URL = "https://api.fedapay.com/v1/transactions"

@csrf_exempt
def connexion_chauffeur(request):
    """ Authentification du chauffeur par téléphone """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # On nettoie le numéro pour ne garder que les chiffres
            tel = "".join(filter(str.isdigit, str(data.get("telephone", ""))))
            chauffeur = Chauffeur.objects.filter(telephone=tel).first()
            
            if chauffeur:
                return JsonResponse(ChauffeurSerializer(chauffeur).data)
            return JsonResponse({"error": "Compte introuvable"}, status=404)
        except Exception:
            return JsonResponse({"error": "Données invalides"}, status=400)
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

@csrf_exempt
def initier_paiement(request, chauffeur_id):
    """ Crée une transaction et génère le lien FedaPay pour Flutter """
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
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
        
        # Création de la transaction sur FedaPay
        r = requests.post(FEDAPAY_URL, json=payload, headers=headers)
        
        if r.status_code not in [200, 201]:
            return JsonResponse({"error": "Erreur d'authentification FedaPay", "details": r.json()}, status=r.status_code)
            
        res_data = r.json()
        transaction = res_data.get('v1/transaction') or res_data.get('transaction') or res_data
        trans_id = transaction.get('id')
        
        # Génération du Token pour l'URL Checkout
        token_r = requests.post(f"{FEDAPAY_URL}/{trans_id}/token", headers=headers)
        url_paiement = token_r.json().get('url') or token_r.json().get('v1/token', {}).get('url')
        
        return JsonResponse({"url": url_paiement})
            
    except Chauffeur.DoesNotExist:
        return JsonResponse({"error": "Chauffeur inconnu"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    """ Mise à jour GPS et Statut (C'est cette URL que Flutter appelle) """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            
            # Mise à jour des champs si présents dans le JSON
            if "latitude" in data: chauffeur.latitude = data["latitude"]
            if "longitude" in data: chauffeur.longitude = data["longitude"]
            if "est_en_ligne" in data: chauffeur.est_en_ligne = data["est_en_ligne"]
            
            chauffeur.save()
            return JsonResponse({"status": "success", "est_en_ligne": chauffeur.est_en_ligne})
        except Chauffeur.DoesNotExist:
            return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "POST requis"}, status=405)

def profil_chauffeur(request, chauffeur_id):
    """ Utilisé par Flutter pour vérifier si le compte est devenu ACTIF après paiement """
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        return JsonResponse(ChauffeurSerializer(chauffeur).data)
    except Chauffeur.DoesNotExist:
        return JsonResponse({"error": "Profil non trouvé"}, status=404)

def liste_taxis_actifs(request):
    """ Pour la carte client : renvoie les taxis qui ont payé ET sont en ligne """
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    serializer = ChauffeurSerializer(taxis, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def fedapay_webhook(request):
    """ Activation automatique suite au succès du paiement FedaPay """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            if data.get('event') == 'transaction.approved':
                entity = data.get('entity', {})
                phone = entity.get('customer', {}).get('phone_number', {}).get('number')
                
                # On cherche le chauffeur par son numéro de téléphone
                chauffeur = Chauffeur.objects.filter(telephone__contains=phone).first()
                if chauffeur:
                    chauffeur.est_actif = True
                    chauffeur.save()
                    return HttpResponse("Compte Activé", status=200)
        except Exception:
            pass
    return HttpResponse("Signal ignoré", status=200)