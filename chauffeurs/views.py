import json
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur

# --- CONFIGURATION PAYTECH ---
PAYTECH_API_KEY = "TA_CLE_API"
PAYTECH_API_SECRET = "TON_SECRET_API"
PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"

# 1. CONNEXION DU CHAUFFEUR (Sécurisée contre l'erreur 500)
@csrf_exempt
def connexion_chauffeur(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # On récupère le téléphone et on enlève les espaces
            telephone_saisi = str(data.get("telephone", "")).strip()
            
            if not telephone_saisi:
                return JsonResponse({"error": "Numéro vide"}, status=400)

            # Recherche du chauffeur
            chauffeur = Chauffeur.objects.filter(telephone=telephone_saisi).first()
            
            if chauffeur:
                # On vérifie dynamiquement si le champ est 'service' ou 'est_actif'
                etat_abonnement = getattr(chauffeur, 'service', getattr(chauffeur, 'est_actif', False))
                
                return JsonResponse({
                    "id": chauffeur.id,
                    "nom_complet": getattr(chauffeur, 'nom_complet', 'Chauffeur'),
                    "telephone": chauffeur.telephone,
                    "est_actif": etat_abonnement,
                }, status=200)
            else:
                return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)
        
        except Exception as e:
            # En cas de crash, on renvoie l'erreur précise pour debugger
            return JsonResponse({"error": f"Crash Serveur: {str(e)}"}, status=500)
            
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

# 2. INITIALISATION DU PAIEMENT PAYTECH
@csrf_exempt
def initier_paiement(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        
        payload = {
            "item_name": "Abonnement Mensuel N'WÉLÉ",
            "item_price": "10000",
            "currency": "XOF",
            "ref_command": f"ABO_{chauffeur.id}",
            "command_name": f"Abonnement de {chauffeur.nom_complet}",
            "env": "test", 
            "ipn_url": "https://nwele-api.onrender.com/api/paytech-callback/",
            "success_url": "https://nwele-api.onrender.com/paiement-reussi/",
            "cancel_url": "https://nwele-api.onrender.com/paiement-annule/",
            "custom_field": json.dumps({"chauffeur_id": chauffeur.id})
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "API_KEY": PAYTECH_API_KEY,
            "API_SECRET": PAYTECH_API_SECRET
        }

        response = requests.post(PAYTECH_URL, json=payload, headers=headers)
        res_data = response.json()

        if res_data.get("success") == 1:
            return JsonResponse({"url": res_data["token_url"]})
        else:
            return JsonResponse({"error": "Erreur PayTech"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# 3. CALLBACK IPN (Validation automatique du paiement)
@csrf_exempt
def paytech_callback(request):
    if request.method == "POST":
        try:
            # On essaye de récupérer l'ID depuis plusieurs sources possibles de PayTech
            chauffeur_id = request.POST.get('item_id') or request.POST.get('ref_command')
            
            if chauffeur_id and "ABO_" in str(chauffeur_id):
                real_id = chauffeur_id.replace("ABO_", "")
                chauffeur = Chauffeur.objects.get(id=real_id)
                # On active le champ 'service'
                if hasattr(chauffeur, 'service'):
                    chauffeur.service = True
                elif hasattr(chauffeur, 'est_actif'):
                    chauffeur.est_actif = True
                chauffeur.save()
                return HttpResponse("OK", status=200)
            
            return HttpResponse("ID non trouvé", status=400)
        except Exception as e:
            return HttpResponse(f"Erreur: {e}", status=200) # 200 pour stopper les essais PayTech
    return HttpResponse(status=405)

# 4. PROFIL (Surveillé par Flutter pour redirection automatique)
def profil_chauffeur(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        etat = getattr(chauffeur, 'service', getattr(chauffeur, 'est_actif', False))
        return JsonResponse({
            "id": chauffeur.id,
            "est_actif": etat,
        })
    except:
        return JsonResponse({"error": "Inconnu"}, status=404)

# 5. UPDATE GPS
@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            chauffeur.lat = data.get("lat")
            chauffeur.lng = data.get("lng")
            chauffeur.est_en_ligne = data.get("est_en_ligne", False)
            chauffeur.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)