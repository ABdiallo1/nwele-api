import requests
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur
from .serializers import ChauffeurSerializer

# CONFIGURATION FEDAPAY
# Remplace par ta vraie clé sk_sandbox_...
FEDAPAY_API_KEY = "sk_sandbox_JVBu9SjQL5rl3Ka4_muQ0J4h" 
FEDAPAY_URL = "https://api.fedapay.com/v1/transactions"

@csrf_exempt
def connexion_chauffeur(request):
    """ Authentification du chauffeur par téléphone """
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
    """ Génère le lien de paiement FedaPay """
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        
        payload = {
            "description": f"Abonnement N'WÉLÉ - {chauffeur.nom_complet}",
            "amount": 100, # Montant de test
            "currency": {"iso": "XOF"},
            "callback_url": f"https://nwele-api.onrender.com/api/profil-chauffeur/{chauffeur.id}/",
            "customer": {
                "firstname": chauffeur.nom_complet,
                "lastname": "Chauffeur",
                "email": f"taxi{chauffeur.id}@nwele.com",
                "phone_number": {"number": chauffeur.telephone, "country": "ml"}
            }
        }
        
        headers = {"Authorization": f"Bearer {FEDAPAY_API_KEY}", "Content-Type": "application/json"}
        
        # 1. Création de la transaction
        r = requests.post(FEDAPAY_URL, json=payload, headers=headers)
        if r.status_code not in [200, 201]:
            return JsonResponse({"error": "Erreur lors de la création FedaPay"}, status=400)
            
        res_data = r.json()
        trans_id = res_data['v1/transaction']['id']
        
        # 2. Génération du lien de redirection (Token)
        token_r = requests.post(f"{FEDAPAY_URL}/{trans_id}/token", headers=headers)
        return JsonResponse({"url": token_r.json()['url']})
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def fedapay_webhook(request):
    """ 
    URL de notification (IPN) : Active l'abonnement quand le paiement est fini.
    À configurer dans ton Dashboard FedaPay (URL de notification).
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # FedaPay envoie l'événement 'transaction.approved'
            if data.get('event') == 'transaction.approved':
                transaction = data.get('entity', {})
                # On récupère le téléphone du client pour retrouver le chauffeur
                phone = transaction.get('customer', {}).get('phone_number', {}).get('number')
                chauffeur = Chauffeur.objects.filter(telephone=phone).first()
                if chauffeur:
                    chauffeur.enregistrer_paiement()
                    return HttpResponse("OK")
        except Exception:
            pass
    return HttpResponse("Invalide", status=200)

def profil_chauffeur(request, chauffeur_id):
    """ Renvoie les infos d'un chauffeur """
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        return JsonResponse(ChauffeurSerializer(chauffeur).data)
    except Exception:
        return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)

@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    """ Mise à jour GPS, Statut et Plaque depuis Flutter """
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
    """ Pour l'écran carte des clients """
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    return JsonResponse(ChauffeurSerializer(taxis, many=True).data, safe=False)