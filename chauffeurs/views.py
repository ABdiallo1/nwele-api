import json
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur  # Assure-toi que ton modèle s'appelle bien Chauffeur

# --- CONFIGURATION PAYTECH ---
PAYTECH_API_KEY = "TON_API_KEY"
PAYTECH_API_SECRET = "TON_API_SECRET"
PAYTECH_URL = "https://paytech.sn/api/payment/request-payment"

# 1. CONNEXION DU CHAUFFEUR
@csrf_exempt
def connexion_chauffeur(request):
    if request.method == "POST":
        data = json.loads(request.body)
        telephone = data.get("telephone")
        
        try:
            chauffeur = Chauffeur.objects.get(telephone=telephone)
            return JsonResponse({
                "id": chauffeur.id,
                "nom_complet": chauffeur.nom_complet,
                "telephone": chauffeur.telephone,
                "est_actif": chauffeur.service  # 'service' est ton champ booléen pour l'abonnement
            })
        except Chauffeur.DoesNotExist:
            return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)

# 2. INITIALISATION DU PAIEMENT PAYTECH
@csrf_exempt
def initier_paiement(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        
        payload = {
            "item_name": "Abonnement Mensuel N'WÉLÉ",
            "item_price": "10000",
            "currency": "XOF",
            "ref_command": f"ABO_{chauffeur.id}_{json.dumps(chauffeur.id)}", # Référence unique
            "command_name": f"Abonnement de {chauffeur.nom_complet}",
            "env": "test", # Change en 'prod' pour les vrais paiements
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

    except Chauffeur.DoesNotExist:
        return JsonResponse({"error": "Chauffeur introuvable"}, status=404)

# 3. CALLBACK IPN (Appelé par PayTech après le paiement)
@csrf_exempt
def paytech_callback(request):
    # PayTech envoie les données en POST via IPN
    # C'est ici que le champ 'service' devient True
    try:
        # On peut récupérer l'ID envoyé dans custom_field ou ref_command
        # Note: PayTech envoie les données en tant que Form Data en IPN
        chauffeur_id = request.POST.get('item_id') # Ou analyse le custom_field
        
        # Exemple si tu as mis l'ID dans custom_field :
        # custom_data = json.loads(request.POST.get('custom_field'))
        # chauffeur_id = custom_data['chauffeur_id']

        if chauffeur_id:
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            chauffeur.service = True  # L'abonnement est activé
            chauffeur.save()
            return HttpResponse("OK", status=200)
            
    except Exception as e:
        print(f"Erreur Callback: {e}")
        return HttpResponse("Erreur", status=400)

# 4. PROFIL (Vérifié par Flutter pour la redirection automatique)
def profil_chauffeur(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        return JsonResponse({
            "id": chauffeur.id,
            "nom_complet": chauffeur.nom_complet,
            "est_actif": chauffeur.service, # Flutter surveille ce champ
            "telephone": chauffeur.telephone
        })
    except Chauffeur.DoesNotExist:
        return JsonResponse({"error": "Introuvable"}, status=404)

# 5. MISE À JOUR GPS ET STATUT EN LIGNE
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