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

# On importe les modèles et sérialiseurs locaux
from .models import Chauffeur
from .serializers import ChauffeurSerializer

# --- 1. ADMINISTRATION ---
class ChauffeurViewSet(viewsets.ModelViewSet):
    """Interface d'administration pour gérer les chauffeurs via DRF."""
    queryset = Chauffeur.objects.all()
    serializer_class = ChauffeurSerializer

# --- 2. ESPACE CLIENT (PASSAGER) ---
@api_view(['GET'])
@permission_classes([AllowAny])
def liste_taxis(request):
    """Liste les chauffeurs actifs et en ligne (nettoyage automatique des expirés)."""
    maintenant = timezone.now()
    
    # Sécurité : On désactive ceux dont l'abonnement a expiré avant d'afficher la liste
    Chauffeur.objects.filter(date_expiration__lt=maintenant, est_actif=True).update(
        est_actif=False, 
        est_en_ligne=False
    )
    
    taxis = Chauffeur.objects.filter(est_en_ligne=True, est_actif=True)
    serializer = ChauffeurSerializer(taxis, many=True)
    return Response(serializer.data)

# --- 3. ESPACE CHAUFFEUR (LOGIN & PROFIL) ---
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
        return Response({"error": "Chauffeur non trouvé"}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def profil_chauffeur(request, pk):
    try:
        chauffeur = Chauffeur.objects.get(pk=pk)
        return Response(ChauffeurSerializer(chauffeur).data)
    except Chauffeur.DoesNotExist:
        return Response({"error": "Profil introuvable"}, status=404)

@api_view(['PATCH', 'PUT'])
@permission_classes([AllowAny])
def mettre_a_jour_chauffeur(request, pk):
    try:
        chauffeur = Chauffeur.objects.get(pk=pk)
        serializer = ChauffeurSerializer(chauffeur, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Chauffeur.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# --- 4. SYSTÈME DE PAIEMENT PAYTECH ---

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def creer_lien_paytech(request):
    """Génère un lien de paiement PayTech pour le chauffeur."""
    telephone = request.query_params.get('telephone') if request.method == 'GET' else request.data.get('telephone')
    
    if not telephone:
        return Response({'error': 'Le numéro de téléphone est requis'}, status=400)
    
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        
        payload = {
            "item_name": "Abonnement Mensuel NWELE",
            "item_price": "10000",
            "currency": "XOF",
            "ref_command": f"NWELE-{str(uuid.uuid4())[:8]}",
            "env": "test",  # Changez en 'prod' pour la production
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
        
    except Chauffeur.DoesNotExist:
        return Response({'error': 'Chauffeur inconnu'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def paytech_webhook(request):
    """IPN : Reçoit la confirmation automatique de PayTech."""
    data = request.data
    custom_field_raw = data.get('custom_field')
    price = data.get('item_price')
    
    if custom_field_raw and str(price) == "10000":
        try:
            # Sécurité : On gère le JSON string ou dictionnaire
            field = json.loads(custom_field_raw) if isinstance(custom_field_raw, str) else custom_field_raw
            
            chauffeur_id = field.get('chauffeur_id')
            c = Chauffeur.objects.get(id=chauffeur_id)
            
            # Activation du compte (Logique définie dans models.py)
            c.enregistrer_paiement() 
            return Response({"status": "SUCCESS"}, status=200)
        except Exception as e:
            return Response({"status": "ERROR", "message": str(e)}, status=400)
            
    return Response({"status": "INVALID_PAYLOAD"}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def verifier_statut(request, id):
    """Page HTML simple de confirmation après paiement."""
    try:
        c = Chauffeur.objects.get(id=id)
        msg = "Félicitations ! Votre compte est maintenant ACTIF." if c.est_actif else "Paiement en attente de traitement..."
        return HttpResponse(f"""
            <html>
                <head><meta charset="utf-8"></head>
                <body style='text-align:center; font-family:sans-serif; padding:50px; background:#f4f4f4;'>
                    <div style='background:white; padding:30px; border-radius:15px; display:inline-block; border:1px solid #ddd;'>
                        <h1 style='color:#f1c40f;'>{c.nom}</h1>
                        <p style='font-size:1.2em;'>{msg}</p>
                        <hr>
                        <p>Vous pouvez maintenant fermer cette page et retourner dans l'application.</p>
                    </div>
                </body>
            </html>
        """)
    except:
        return HttpResponse("Erreur lors de la vérification", status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
def valider_paiement_manuel(request, chauffeur_id):
    """Force l'activation d'un chauffeur sans passer par PayTech."""
    try:
        c = Chauffeur.objects.get(id=chauffeur_id)
        c.enregistrer_paiement()
        return Response({"message": f"Le compte de {c.nom} a été activé manuellement."})
    except:
        return Response({"error": "Chauffeur non trouvé"}, status=404)