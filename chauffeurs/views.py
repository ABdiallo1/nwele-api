import os, requests, json, time
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .models import Chauffeur

# --- MISE À JOUR DU STATUT (UTILISÉ PAR LE DASHBOARD) ---
@api_view(['POST'])
def mettre_a_jour_chauffeur(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    # On récupère 'est_en_ligne' envoyé par Flutter
    est_en_ligne = request.data.get('est_en_ligne')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')

    if est_en_ligne is not None: 
        chauffeur.est_en_ligne = est_en_ligne
    if latitude is not None: chauffeur.latitude = latitude
    if longitude is not None: chauffeur.longitude = longitude
    
    chauffeur.save()
    return Response({"status": "Mis à jour", "est_en_ligne": chauffeur.est_en_ligne})

# --- PROFIL (UTILISÉ POUR VÉRIFIER L'ACTIVATION) ---
@api_view(['GET'])
def ChauffeurProfilView(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    return Response({
        "id": chauffeur.id,
        "nom_complet": chauffeur.nom_complet,
        "est_actif": chauffeur.est_actif,
        "est_en_ligne": chauffeur.est_en_ligne,
        "jours_restants": chauffeur.jours_restants,
        "date_expiration": str(chauffeur.date_expiration)
    })

# --- INITIALISATION DU PAIEMENT ---
@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    API_KEY = "4708a871b0d511a24050685ff7abfab2e68c69032e1b3d2913647ef46ed656f2" 
    API_SECRET = "17cb57b72f679c40ab29eedfcd485bea81582adb770882a78525abfdc57e6784"
    
    url = "https://paytech.sn/api/payment/request-payment"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "API_KEY": API_KEY,
        "API_SECRET": API_SECRET,
    }
    
    payload = {
        "item_name": "Abonnement Taxi N'WELE",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": f"NWELE-{chauffeur.id}-{int(time.time())}", 
        "command_name": f"Paiement de {chauffeur.nom_complet}",
        "env": "test", 
        "ipn_url": "https://nwele-api.onrender.com/api/paiement/callback/",
        "success_url": "https://nwele-api.onrender.com/api/paiement-succes/",
        "cancel_url": "https://nwele-api.onrender.com/api/paiement-succes/",
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        if response.status_code == 200 and res_data.get('success') == 1:
            return Response({"url": res_data['redirect_url']}, status=200)
        return Response({"error": res_data.get('errors', 'Erreur PayTech')}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# --- CALLBACK IPN (RÉCEPTION DU PAIEMENT) ---
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def PaytechCallbackView(request):
    ref = request.data.get('ref_command')
    if ref:
        try:
            c_id = ref.split('-')[1]
            chauffeur = Chauffeur.objects.get(id=c_id)
            chauffeur.enregistrer_paiement()
            return Response({"status": "ok"})
        except: pass
    return Response({"status": "error"}, status=400)

def paiement_succes(request):
    return HttpResponse("<html><body style='text-align:center;padding-top:50px;'><h1>✅ Paiement Reçu !</h1><p>Retournez dans l'app et cliquez sur ACTIVER.</p></body></html>")