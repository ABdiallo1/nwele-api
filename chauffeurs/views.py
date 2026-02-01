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

# --- 1. ADMINISTRATION (DRF) ---
class ChauffeurViewSet(viewsets.ModelViewSet):
    queryset = Chauffeur.objects.all()
    serializer_class = ChauffeurSerializer

# --- 2. ESPACE CLIENT (PASSAGER) ---
@api_view(['GET'])
@permission_classes([AllowAny])
def liste_taxis(request):
    maintenant = timezone.now()
    # Désactivation automatique si l'abonnement est expiré
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
            "telephone": chauffeur.telephone,
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

# --- 4. SYSTEME DE PAIEMENT (PAYTECH) ---

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def creer_lien_paytech(request):
    """
    Crée une demande de paiement auprès de PayTech.
    Utilisez "env": "test" pour vos tests sans frais réels.
    """
    telephone = request.query_params.get('telephone') if request.method == 'GET' else request.data.get('telephone')
    
    if not telephone:
        return Response({'error': 'Numero telephone requis'}, status=400)
    
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        BASE_URL = "https://nwele-api.onrender.com"
        
        payload = {
            "item_name": "Abonnement Mensuel N'WELE",
            "item_price": "10000",
            "currency": "XOF",
            "ref_command": f"CMD-{uuid.uuid4().hex[:8]}",
            "env": "test", # <--- RESTER EN TEST POUR VOS ESSAIS
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
    """
    WEBHOOK : Reçoit la confirmation de PayTech.
    Vérifie strictement le montant pour éviter les validations partielles.
    """
    custom_field = request.data.get('custom_field')
    # PayTech renvoie le prix de l'item dans item_price
    montant_recu = request.data.get('item_price') 

    # Vérification : Doit avoir le bon ID de chauffeur ET le montant de 10.000
    if custom_field and montant_recu == "10000":
        try:
            field_data = json.loads(custom_field)
            chauffeur_id = field_data.get('chauffeur_id')
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            
            # On active le chauffeur uniquement si les 10.000 sont confirmés
            chauffeur.enregistrer_paiement()
            print(f"--- PAIEMENT VALIDE : {chauffeur.nom} est actif ---")
            return Response({"status": "success"}, status=200)
            
        except (Chauffeur.DoesNotExist, json.JSONDecodeError) as e:
            return Response({"error": "Donnees invalides"}, status=400)
    
    print(f"--- TENTATIVE DE PAIEMENT INVALIDE : Montant recu {montant_recu} ---")
    return Response({"error": "Montant incorrect ou transaction invalide"}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def verifier_statut(request, id):
    """Page de redirection après paiement"""
    try:
        chauffeur = Chauffeur.objects.get(id=id)
        return HttpResponse(f"""
            <div style="text-align:center; padding:50px; font-family:sans-serif;">
                <h1 style="color:green;">Paiement en cours...</h1>
                <p>Merci {chauffeur.nom}. Dès que l'opérateur confirme les 10.000 FCFA, 
                votre compte sera activé automatiquement.</p>
                <p>Vous pouvez fermer cette page et retourner sur l'application.</p>
            </div>
        """)
    except Chauffeur.DoesNotExist:
        return HttpResponse("Chauffeur introuvable", status=404)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def valider_paiement_manuel(request, chauffeur_id):
    """Forcer l'activation si besoin (Admin)"""
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        chauffeur.enregistrer_paiement()
        return Response({"message": f"Validation manuelle réussie pour {chauffeur.nom}"})
    except Chauffeur.DoesNotExist:
        return Response({"error": "Introuvable"}, status=404)