from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json
import requests
import uuid

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Chauffeur
from .serializers import ChauffeurSerializer

# --- 1. ADMINISTRATION ---
class ChauffeurViewSet(viewsets.ModelViewSet):
    queryset = Chauffeur.objects.all()
    serializer_class = ChauffeurSerializer

# --- 2. ESPACE CLIENT ---
@api_view(['GET'])
@permission_classes([AllowAny])
def liste_taxis(request):
    maintenant = timezone.now()
    Chauffeur.objects.filter(date_expiration__lt=maintenant, est_actif=True).update(est_actif=False, est_en_ligne=False)
    
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
        return Response({"error": "Inconnu"}, status=404)

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

# --- 4. PAIEMENT PAYTECH ---
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def creer_lien_paytech(request):
    telephone = request.query_params.get('telephone') if request.method == 'GET' else request.data.get('telephone')
    if not telephone:
        return Response({'error': 'Manquant'}, status=400)
    
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        payload = {
            "item_name": "Abonnement NWELE",
            "item_price": "10000",
            "currency": "XOF",
            "ref_command": str(uuid.uuid4())[:8],
            "env": "test", # MODE TEST ACTIF
            "custom_field": json.dumps({"chauffeur_id": chauffeur.id}),
            "success_url": f"https://nwele-api.onrender.com/api/verifier-statut/{chauffeur.id}/",
            "ipn_url": "https://nwele-api.onrender.com/api/paytech-webhook/"
        }
        headers = {
            "API_KEY": "4708a871b0d511a24050685ff7abfab2e68c69032e1b3d2913647ef46ed656f2",
            "API_SECRET": "17cb57b72f679c40ab29eedfcd485bea81582adb770882a78525abfdc57e6784"
        }
        r = requests.post("https://paytech.sn/api/payment/request-payment", data=payload, headers=headers)
        return Response(r.json())
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def paytech_webhook(request):
    data = request.data
    custom_field = data.get('custom_field')
    price = data.get('item_price')
    
    if custom_field and str(price) == "10000":
        try:
            field = json.loads(custom_field)
            c = Chauffeur.objects.get(id=field.get('chauffeur_id'))
            c.enregistrer_paiement()
            return Response({"status": "ok"})
        except:
            pass
    return Response({"status": "fail"}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def verifier_statut(request, id):
    try:
        c = Chauffeur.objects.get(id=id)
        msg = "Active !" if c.est_actif else "En attente..."
        return HttpResponse(f"<h1>{c.nom}</h1><p>Statut : {msg}</p>")
    except:
        return HttpResponse("Erreur", status=404)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def valider_paiement_manuel(request, chauffeur_id):
    try:
        c = Chauffeur.objects.get(id=chauffeur_id)
        c.enregistrer_paiement()
        return Response({"msg": "OK"})
    except:
        return Response(status=404)