from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json
import requests
import uuid

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Chauffeur
from .serializers import ChauffeurSerializer

# --- 1. ADMINISTRATION ---
class ChauffeurViewSet(viewsets.ModelViewSet):
    queryset = Chauffeur.objects.all()
    serializer_class = ChauffeurSerializer

# --- 2. LISTE DES TAXIS (POUR LES CLIENTS) ---
@api_view(['GET'])
@permission_classes([AllowAny])
def liste_taxis(request):
    maintenant = timezone.now()
    # Désactiver automatiquement les chauffeurs dont l'abonnement a expiré
    Chauffeur.objects.filter(date_expiration__lt=maintenant, est_en_ligne=True).update(est_en_ligne=False, est_actif=False)

    seuil_temps = maintenant - timedelta(minutes=5)
    taxis = Chauffeur.objects.filter(est_en_ligne=True, est_actif=True, updated_at__gte=seuil_temps)
    
    data = [{
        "id": t.id,
        "nom": t.nom,
        "telephone": t.telephone,
        "latitude": t.latitude,
        "longitude": t.longitude,
        "plaque": t.plaque_immatriculation,
    } for t in taxis]
    return Response(data)

# --- 3. CRÉATION DU LIEN DE PAIEMENT PAYTECH ---
@api_view(['GET', 'POST']) # Accepte GET pour tes tests navigateur et POST pour Flutter
@permission_classes([AllowAny])
def creer_chauffeur_manuel(request):
    """
    Génère un lien de paiement PayTech pour un chauffeur via son numéro de téléphone.
    """
    # Récupération du téléphone : soit via l'URL (GET), soit via le corps de requête (POST)
    telephone = request.query_params.get('telephone') if request.method == 'GET' else request.data.get('telephone')

    if not telephone:
        return Response({'error': 'Veuillez fournir un numéro de téléphone (?telephone=...)'}, status=400)

    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        BASE_URL = "https://nwele-api.onrender.com"
        
        payload = {
            "item_name": f"Abonnement Taxi N'WELE - {chauffeur.nom}",
            "item_price": "10000",
            "currency": "XOF",
            "ref_command": str(uuid.uuid4())[:8],
            "env": "test", 
            "custom_field": json.dumps({"chauffeur_id": chauffeur.id}),
            "success_url": f"{BASE_URL}/api/verifier-statut/{chauffeur.id}/", 
            "ipn_url": f"{BASE_URL}/api/paytech-webhook/"
        }
        headers = {
            "Accept": "application/json", 
            "API_KEY": "4708a871b0d511a24050685ff7abfab2e68c69032e1b3d2913647ef46ed656f2", 
            "API_SECRET": "17cb57b72f679c40ab29eedfcd485bea81582adb770882a78525abfdc57e6784"
        }
        
        response = requests.post("https://paytech.sn/api/payment/request-payment", data=payload, headers=headers)
        return Response(response.json())

    except Chauffeur.DoesNotExist:
        return Response({'error': f'Chauffeur avec le numéro {telephone} introuvable'}, status=404)

# --- 4. WEBHOOK PAYTECH (IPN) ---
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def paytech_webhook(request):
    custom_field = request.data.get('custom_field')
    if custom_field:
        try:
            field_data = json.loads(custom_field)
            chauffeur = Chauffeur.objects.get(id=field_data.get('chauffeur_id'))
            chauffeur.enregistrer_paiement() # Active l'abonnement dans ton modèle
            return Response({"message": "OK"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
    return Response({"error": "Data manquante"}, status=400)

# --- 5. VÉRIFICATION DU STATUT ET CONNEXION ---
@api_view(['GET'])
@permission_classes([AllowAny])
def verifier_statut(request, id):
    try:
        chauffeur = Chauffeur.objects.get(id=id)
        chauffeur.verifier_statut_abonnement() 
        return HttpResponse(f"<h1>Succès</h1><p>Merci {chauffeur.nom}, votre compte est actif !</p>")
    except Chauffeur.DoesNotExist:
        return HttpResponse("Chauffeur introuvable", status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone')
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        chauffeur.verifier_statut_abonnement()
        return Response({
            "id": chauffeur.id,
            "nom": chauffeur.nom,
            "est_actif": chauffeur.est_actif,
            "jours_restants": chauffeur.jours_restants(),
        })
    except Chauffeur.DoesNotExist:
        return Response({"error": "Inconnu"}, status=404)

# --- 6. ACTIONS MANUELLES ---
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def creer_compte_chauffeur(request):
    serializer = ChauffeurSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def valider_paiement_manuel(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        chauffeur.enregistrer_paiement() 
        return HttpResponse(f"Compte de {chauffeur.nom} activé.")
    except:
        return HttpResponse("Erreur", status=404)