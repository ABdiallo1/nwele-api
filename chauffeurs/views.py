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

# --- 2. LISTE DES TAXIS ---
@api_view(['GET'])
@permission_classes([AllowAny])
def liste_taxis(request):
    maintenant = timezone.now()
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

# --- 3. GESTION DES PROFILS (Requis par urls.py) ---
@api_view(['GET'])
@permission_classes([AllowAny])
def profil_chauffeur(request, pk):
    try:
        chauffeur = Chauffeur.objects.get(pk=pk)
        return Response(ChauffeurSerializer(chauffeur).data)
    except Chauffeur.DoesNotExist:
        return Response(status=404)

@api_view(['POST', 'PUT', 'PATCH'])
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
        return Response({"status": "deconnecte"})
    except Chauffeur.DoesNotExist:
        return Response(status=404)

# --- 4. PAIEMENT PAYTECH ---
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def creer_chauffeur_manuel(request):
    telephone = request.query_params.get('telephone') if request.method == 'GET' else request.data.get('telephone')
    if not telephone:
        return Response({'error': 'Telephone requis'}, status=400)
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        BASE_URL = "https://nwele-api.onrender.com"
        payload = {
            "item_name": f"Abonnement - {chauffeur.nom}",
            "item_price": "10000",
            "currency": "XOF",
            "ref_command": str(uuid.uuid4())[:8],
            "env": "test", 
            "custom_field": json.dumps({"chauffeur_id": chauffeur.id}),
            "success_url": f"{BASE_URL}/api/verifier-statut/{chauffeur.id}/", 
            "ipn_url": f"{BASE_URL}/api/paytech-webhook/"
        }
        headers = {"API_KEY": "4708a871b0d511a24050685ff7abfab2e68c69032e1b3d2913647ef46ed656f2", "API_SECRET": "17cb57b72f679c40ab29eedfcd485bea81582adb770882a78525abfdc57e6784"}
        response = requests.post("https://paytech.sn/api/payment/request-payment", data=payload, headers=headers)
        return Response(response.json())
    except Chauffeur.DoesNotExist:
        return Response({'error': 'Chauffeur introuvable'}, status=404)

# --- 5. AUTRES FONCTIONS (Vides pour eviter les erreurs de build) ---
@api_view(['POST'])
def creer_paiement(request): return Response({"detail": "Pas encore implemente"})

@api_view(['POST'])
def valider_manuel(request, chauffeur_id): return Response({"detail": "Pas encore implemente"})

@api_view(['GET'])
@permission_classes([AllowAny])
def verifier_statut(request, id):
    try:
        chauffeur = Chauffeur.objects.get(id=id)
        chauffeur.verifier_statut_abonnement() 
        return HttpResponse(f"<h1>Succes</h1><p>Compte de {chauffeur.nom} active.</p>")
    except Chauffeur.DoesNotExist: return HttpResponse("Introuvable", status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
def paytech_webhook(request):
    data = request.data
    custom_field = data.get('custom_field')
    if custom_field:
        try:
            field_data = json.loads(custom_field)
            chauffeur = Chauffeur.objects.get(id=field_data.get('chauffeur_id'))
            chauffeur.enregistrer_paiement()
            return Response({"status": "success"})
        except: pass
    return Response({"error": "No data"}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone')
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        return Response({"id": chauffeur.id, "nom": chauffeur.nom, "est_actif": chauffeur.est_actif})
    except Chauffeur.DoesNotExist: return Response(status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def creer_compte_chauffeur(request):
    serializer = ChauffeurSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)