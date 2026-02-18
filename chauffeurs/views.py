import requests
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur
from .serializers import ChauffeurSerializer

# CONFIGURATION FEDAPAY
# Utilisation de ta clé sandbox vérifiée
FEDAPAY_API_KEY = "sk_sandbox_JVBu9SjQL5rl3Ka4_muQ0J4h" 
FEDAPAY_URL = "https://api.fedapay.com/v1/transactions"

@csrf_exempt
def connexion_chauffeur(request):
    """ Authentification du chauffeur par téléphone """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # On nettoie le numéro pour la recherche
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
    """ Prépare la transaction FedaPay et renvoie le lien de paiement """
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        
        # Nettoyage strict du numéro : uniquement les chiffres
        tel_propre = "".join(filter(str.isdigit, str(chauffeur.telephone)))
        
        payload = {
            "description": f"Abonnement N'WÉLÉ - {chauffeur.nom_complet}",
            "amount": 100, # Montant de test (100 XOF)
            "currency": {"iso": "XOF"},
            "callback_url": f"https://nwele-api.onrender.com/api/profil-chauffeur/{chauffeur.id}/",
            "customer": {
                "firstname": chauffeur.nom_complet,
                "lastname": "Chauffeur",
                "email": f"chauffeur{chauffeur.id}@nwele.com", # Email dynamique unique
                "phone_number": {"number": tel_propre, "country": "ml"} # 'ml' pour Mali
            }
        }
        
        headers = {
            "Authorization": f"Bearer {FEDAPAY_API_KEY}", 
            "Content-Type": "application/json"
        }
        
        # 1. Création de la transaction sur FedaPay
        r = requests.post(FEDAPAY_URL, json=payload, headers=headers)
        res_data = r.json()
        
        if r.status_code not in [200, 201]:
            return JsonResponse({
                "error": "FedaPay Reject", 
                "details": res_data 
            }, status=400)
            
        # 2. Extraction sécurisée de l'ID (FedaPay encapsule parfois dans 'v1/transaction')
        transaction_obj = res_data.get('v1/transaction', res_data)
        trans_id = transaction_obj.get('id')
        
        # 3. Génération du Token de redirection
        token_r = requests.post(f"{FEDAPAY_URL}/{trans_id}/token", headers=headers)
        return JsonResponse({"url": token_r.json().get('url')})
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def fedapay_webhook(request):
    """ Webhook pour l'activation automatique après paiement réussi """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Vérification de l'événement de succès
            if data.get('event') == 'transaction.approved':
                transaction = data.get('entity', {})
                customer = transaction.get('customer', {})
                phone = customer.get('phone_number', {}).get('number')
                
                # On retrouve le chauffeur par son téléphone
                chauffeur = Chauffeur.objects.filter(telephone=phone).first()
                if chauffeur:
                    chauffeur.enregistrer_paiement() # Appelle ta méthode du modèle
                    return HttpResponse("OK")
        except Exception:
            pass
    return HttpResponse("Invalide", status=200)

def profil_chauffeur(request, chauffeur_id):
    """ Détails du profil pour Flutter """
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        return JsonResponse(ChauffeurSerializer(chauffeur).data)
    except Exception:
        return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)

@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    """ Mise à jour GPS et Statut via Flutter """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            
            # Mise à jour sélective des champs
            if "latitude" in data: chauffeur.latitude = data["latitude"]
            if "longitude" in data: chauffeur.longitude = data["longitude"]
            if "est_en_ligne" in data: chauffeur.est_en_ligne = data["est_en_ligne"]
            if "plaque_immatriculation" in data: 
                chauffeur.plaque_immatriculation = data["plaque_immatriculation"]
            
            chauffeur.save()
            return JsonResponse({"status": "success"})
        except Exception:
            return JsonResponse({"error": "Erreur lors de la mise à jour"}, status=400)
    return JsonResponse({"error": "POST requis"}, status=405)

def liste_taxis_actifs(request):
    """ Liste pour la carte côté Client """
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    return JsonResponse(ChauffeurSerializer(taxis, many=True).data, safe=False)