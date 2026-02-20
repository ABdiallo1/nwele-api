import os, requests, json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur
from .serializers import ChauffeurSerializer
import fedapay
from django.http import JsonResponse

FEDAPAY_API_KEY = os.environ.get('FEDAPAY_API_KEY', 'sk_sandbox_JVBu9SjQL5rl3Ka4_muQ0J4h')
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
        except:
            return JsonResponse({"error": "Erreur données"}, status=400)


def initier_paiement(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        
        # Configuration FedaPay
        fedapay.FedaPay.api_key = "VOTRE_CLE_API_REELLE" # Vérifie bien ta clé !
        fedapay.FedaPay.environment = "sandbox" # ou "live"

        # Création de la transaction
        transaction = fedapay.Transaction.create(
            amount=100,
            currency={'iso': 'XOF'},
            description=f"Abonnement Chauffeur: {chauffeur.nom_complet}",
            customer={
                'firstname': chauffeur.nom_complet,
                'lastname': 'Chauffeur',
                'email': 'chauffeur@taxi.com', # Email fictif obligatoire pour FedaPay
                'phone_number': {'number': chauffeur.telephone, 'country': 'BJ'}
            }
        )
        
        token = transaction.generateToken()
        return JsonResponse({'url': token.url})

    except Chauffeur.DoesNotExist:
        return JsonResponse({'error': 'Chauffeur non trouvé'}, status=404)
    except Exception as e:
        # C'est ici qu'on attrape l'erreur 'NoneType' pour voir ce qui se passe
        print(f"Erreur FedaPay : {str(e)}")
        return JsonResponse({'error': f"Erreur de paiement : {str(e)}"}, status=500)

@csrf_exempt
def update_chauffeur(request, chauffeur_id):
    if request.method == "POST":
        data = json.loads(request.body)
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        if "latitude" in data: chauffeur.latitude = data["latitude"]
        if "longitude" in data: chauffeur.longitude = data["longitude"]
        if "est_en_ligne" in data: chauffeur.est_en_ligne = data["est_en_ligne"]
        chauffeur.save()
        return JsonResponse({"status": "success"})

def liste_taxis_actifs(request):
    taxis = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    return JsonResponse(ChauffeurSerializer(taxis, many=True).data, safe=False)

def profil_chauffeur(request, chauffeur_id):
    chauffeur = Chauffeur.objects.get(id=chauffeur_id)
    return JsonResponse(ChauffeurSerializer(chauffeur).data)