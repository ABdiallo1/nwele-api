import json
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur  # Vérifie que le nom du modèle est correct

# --- CONFIGURATION PAYTECH ---
PAYTECH_API_KEY = "VOTRE_CLE_API"
PAYTECH_API_SECRET = "VOTRE_SECRET_API"
PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"

# 1. CONNEXION DU CHAUFFEUR (Nettoyée et robuste)
@csrf_exempt
def connexion_chauffeur(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # .strip() enlève les espaces accidentels au début ou à la fin
            telephone_saisi = str(data.get("telephone", "")).strip()
            
            # Recherche du chauffeur
            chauffeur = Chauffeur.objects.filter(telephone=telephone_saisi).first()
            
            if chauffeur:
                return JsonResponse({
                    "id": chauffeur.id,
                    "nom_complet": chauffeur.nom_complet,
                    "telephone": chauffeur.telephone,
                    "est_actif": chauffeur.service,  # Ton champ booléen pour l'abonnement
                }, status=200)
            else:
                return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)
        except Exception as e:
            return JsonResponse({"error": "Erreur format JSON"}, status=400)
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
            "env": "test",  # Changez en 'prod' pour le lancement réel
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
            return JsonResponse({"error": "Erreur lors de la création du lien PayTech"}, status=400)

    except Chauffeur.DoesNotExist:
        return JsonResponse({"error": "Chauffeur introuvable"}, status=404)

# 3. CALLBACK IPN (Le serveur PayTech appelle cette fonction)
@csrf_exempt
def paytech_callback(request):
    if request.method == "POST":
        try:
            # PayTech envoie souvent les données en POST direct (Form-data)
            chauffeur_id = request.POST.get('item_id')
            
            # Si item_id est vide, on cherche dans le JSON
            if not chauffeur_id:
                try:
                    data = json.loads(request.body)
                    chauffeur_id = data.get('item_id')
                except:
                    pass

            if chauffeur_id:
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                chauffeur.service = True  # ACTIVATION DU COMPTE
                chauffeur.save()
                return HttpResponse("OK", status=200)
            
            return HttpResponse("ID manquant", status=400)
        except Exception as e:
            # On renvoie 200 même en cas d'erreur log pour éviter que PayTech ne réessaye indéfiniment
            print(f"Erreur IPN: {e}")
            return HttpResponse("Erreur traitée", status=200)
    return HttpResponse(status=405)

# 4. PROFIL (Utilisé pour la redirection automatique dans Flutter)
def profil_chauffeur(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        return JsonResponse({
            "id": chauffeur.id,
            "nom_complet": chauffeur.nom_complet,
            "est_actif": chauffeur.service,
            "telephone": chauffeur.telephone
        })
    except Chauffeur.DoesNotExist:
        return JsonResponse({"error": "Introuvable"}, status=404)

# 5. MISE À JOUR POSITION GPS
@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            
            chauffeur.lat = data.get("lat")
            chauffeur.lng = data.get("lng")
            chauffeur.est_en_ligne = data.get("est_en_ligne")
            chauffeur.save()
            
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)