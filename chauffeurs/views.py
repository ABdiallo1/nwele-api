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

# --- 1. ADMINISTRATION (DRF) ---
class ChauffeurViewSet(viewsets.ModelViewSet):
    queryset = Chauffeur.objects.all()
    serializer_class = ChauffeurSerializer

# --- 2. ESPACE CLIENT ---
@api_view(['GET'])
@permission_classes([AllowAny])
def liste_taxis(request):
    maintenant = timezone.now()
    # Nettoyage automatique des sessions expirées
    Chauffeur.objects.filter(date_expiration__lt=maintenant, est_en_ligne=True).update(est_en_ligne=False, est_actif=False)
    
    taxis = Chauffeur.objects.filter(est_en_ligne=True, est_actif=True)
    serializer = ChauffeurSerializer(taxis, many=True)
    return Response(serializer.data)

# --- 3. ESPACE CHAUFFEUR ---
@api_view(['POST'])
@permission_classes([AllowAny])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone')
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        return Response({
            "id": chauffeur.id,
            "nom": chauffeur.nom,
            "est_actif": chauffeur.est_actif,
            "jours_restants": chauffeur.jours_restants()
        })
    except Chauffeur.DoesNotExist:
        return Response({"error": "Chauffeur inconnu"}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def profil_chauffeur(request, pk):
    try:
        chauffeur = Chauffeur.objects.get(pk=pk)
        return Response(ChauffeurSerializer(chauffeur).data)
    except Chauffeur.DoesNotExist:
        return Response(status=404)

@api_view(['PATCH', 'PUT'])
@permission_classes([AllowAny])
def mettre_a_jour_chauffeur(request, pk):
    try:
        chauffeur = Chauffeur.objects.get(pk=pk)
        serializer = ChauffeurSerializer(chauffeur, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    except Chauffeur.DoesNotExist:
        return Response(status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
def deconnexion_chauffeur(request, pk):
    try:
        chauffeur = Chauffeur.objects.get(pk=pk)
        chauffeur.est_en_ligne = False
        chauffeur.save()
        return Response({"message": "Deconnecte"})
    except Chauffeur.DoesNotExist:
        return Response(status=404)

# --- 4. SYSTEME DE PAIEMENT (PAYTECH) ---
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def creer_chauffeur_manuel(request):
    # Support GET pour test navigateur et POST pour Flutter
    telephone = request.query_params.get('telephone') if request.method == 'GET' else request.data.get('telephone')
    
    if not telephone:
        return Response({'error': 'Numero telephone requis'}, status=400)
    
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        BASE_URL = "https://nwele-api.onrender.com"
        
        payload = {
            "item_name": f"Abonnement N'WELE - {chauffeur.nom}",
            "item_price": "10000",
            "currency": "XOF",
            "ref_command": str(uuid.uuid4())[:8],
            "env": "test",
            "custom_field": json.dumps({"chauffeur_id": chauffeur.id}),
            "success_url": f"{BASE_URL}/api/verifier-statut/{chauffeur.id}/",
            "ipn_url": f"{BASE_URL}/api/paytech-webhook/"
        }
        headers = {
            "API_KEY": "4708a871b0d511a24050685ff7abfab2e68c69032e1b3d2913647ef46ed656f2",
            "API_SECRET": "17cb57b72f679c40ab29eedfcd485bea81582adb770882a78525abfdc57e6784"
        }
        
        response = requests.post("https://paytech.sn/api/payment/request-payment", data=payload, headers=headers)
        return Response(response.json())
    except Chauffeur.DoesNotExist:
        return Response({'error': 'Chauffeur introuvable'}, status=404)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def paytech_webhook(request):
    custom_field = request.data.get('custom_field')
    if custom_field:
        try:
            field_data = json.loads(custom_field)
            chauffeur = Chauffeur.objects.get(id=field_data.get('chauffeur_id'))
            chauffeur.enregistrer_paiement() # Assure-toi que cette methode existe dans models.py
            return Response({"status": "success"})
        except Exception as e:
            return Response({"error": str(e)}, status=400)
    return Response({"error": "No data"}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def verifier_statut(request, id):
    try:
        chauffeur = Chauffeur.objects.get(id=id)
        return HttpResponse(f"<h1>Succes</h1><p>Abonnement de {chauffeur.nom} active !</p>")
    except Chauffeur.DoesNotExist:
        return HttpResponse("Introuvable", status=404)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def valider_paiement_manuel(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        chauffeur.enregistrer_paiement()
        return HttpResponse(f"<h1>Validation manuelle reussie</h1><p>{chauffeur.nom} est actif.</p>")
    except Chauffeur.DoesNotExist:
        return HttpResponse("Chauffeur introuvable", status=404)