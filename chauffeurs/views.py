import json
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur
from .serializers import ChauffeurSerializer
from django.shortcuts import get_object_or_status

# --- CONFIGURATION PAYTECH ---
PAYTECH_API_KEY = "TA_CLE_API"
PAYTECH_API_SECRET = "TON_SECRET_API"

@csrf_exempt
def connexion_chauffeur(request):
    """
    Gère la connexion du chauffeur avec une sécurité totale contre les crashs 500.
    """
    if request.method == "POST":
        try:
            # 1. Chargement et nettoyage des données
            data = json.loads(request.body)
            telephone_saisi = str(data.get("telephone", "")).strip()
            
            if not telephone_saisi:
                return JsonResponse({"error": "Veuillez saisir un numéro"}, status=400)

            # 2. Recherche du chauffeur
            chauffeur = Chauffeur.objects.filter(telephone=telephone_saisi).first()
            
            if chauffeur:
                # 3. Utilisation du Serializer pour transformer l'objet en JSON
                serializer = ChauffeurSerializer(chauffeur)
                return JsonResponse(serializer.data, status=200, safe=False)
            else:
                # Retour 404 si le numéro n'est pas en base
                return JsonResponse({"error": "Chauffeur non trouvé"}, status=404)
        
        except Exception as e:
            # Capture l'erreur exacte pour ne pas avoir une page blanche "Erreur Interne"
            return JsonResponse({"error": f"Erreur Serveur: {str(e)}"}, status=500)
            
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

@csrf_exempt
def initier_paiement(request, chauffeur_id):
    """
    Génère le lien PayTech pour le chauffeur.
    """
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        
        payload = {
            "item_name": "Abonnement N'WÉLÉ",
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

        response = requests.post("https://paytech.sn/api/payment/request-payment", json=payload, headers=headers)
        res_data = response.json()

        if res_data.get("success") == 1:
            return JsonResponse({"url": res_data["token_url"]})
        else:
            return JsonResponse({"error": "Erreur PayTech"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def paytech_callback(request):
    """
    IPN appelé par PayTech pour activer le service automatiquement.
    """
    if request.method == "POST":
        try:
            # On récupère l'ID via le ref_command envoyé plus haut
            ref = request.POST.get('ref_command', "")
            if "ABO_" in ref:
                c_id = ref.replace("ABO_", "")
                chauffeur = Chauffeur.objects.get(id=c_id)
                # On utilise 'service' car c'est ce qui apparaît dans ton admin
                chauffeur.service = True 
                chauffeur.save()
                return HttpResponse("OK", status=200)
        except Exception as e:
            print(f"Erreur Callback: {e}")
            return HttpResponse("Erreur", status=200)
    return HttpResponse(status=405)

def profil_chauffeur(request, chauffeur_id):
    """
    Vérification en temps réel pour la redirection Flutter.
    """
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        serializer = ChauffeurSerializer(chauffeur)
        return JsonResponse(serializer.data)
    except Chauffeur.DoesNotExist:
        return JsonResponse({"error": "Inconnu"}, status=404)

@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    """
    Mise à jour GPS et statut en ligne.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            chauffeur.latitude = data.get("lat", chauffeur.latitude)
            chauffeur.longitude = data.get("lng", chauffeur.longitude)
            chauffeur.est_en_ligne = data.get("est_en_ligne", False)
            chauffeur.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)