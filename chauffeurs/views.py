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

# --- 1. ADMINISTRATION API ---
class ChauffeurViewSet(viewsets.ModelViewSet):
    queryset = Chauffeur.objects.all()
    serializer_class = ChauffeurSerializer

# --- 2. LISTE DES TAXIS POUR LES CLIENTS ---
@api_view(['GET'])
@permission_classes([AllowAny])
def liste_taxis(request):
    maintenant = timezone.now()
    
    # Nettoyage batch : Désactiver les expirés qui sont restés "En ligne"
    Chauffeur.objects.filter(
        date_expiration__lt=maintenant, 
        est_en_ligne=True
    ).update(est_en_ligne=False, est_actif=False)

    seuil_temps = maintenant - timedelta(minutes=5)
    taxis = Chauffeur.objects.filter(
        est_en_ligne=True,
        est_actif=True,
        updated_at__gte=seuil_temps
    )
    
    data = [{
        "id": t.id,
        "nom": t.nom,
        "telephone": t.telephone,
        "latitude": t.latitude,
        "longitude": t.longitude,
        "plaque": t.plaque_immatriculation,
    } for t in taxis]
    return Response(data)

# --- 3. MISE À JOUR POSITION GPS ET STATUT ---
@api_view(['PATCH'])
def mettre_a_jour_chauffeur(request, pk):
    try:
        chauffeur = Chauffeur.objects.get(pk=pk)
        chauffeur.verifier_statut_abonnement()
        
        # Sécurité : Empêcher la mise en ligne si l'abonnement est mort
        if request.data.get('est_en_ligne') is True and not chauffeur.est_actif:
            return Response(
                {"error": "Abonnement expiré. Veuillez recharger."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ChauffeurSerializer(chauffeur, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Chauffeur.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# --- 4. CONNEXION DU CHAUFFEUR ---
@api_view(['POST'])
@permission_classes([AllowAny])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone')
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        chauffeur.verifier_statut_abonnement()
        
        # On renvoie l'objet complet pour que Flutter puisse l'utiliser directement
        return Response({
            "id": chauffeur.id,
            "nom": chauffeur.nom,
            "est_actif": chauffeur.est_actif,
            "est_en_ligne": chauffeur.est_en_ligne,
            "date_expiration": chauffeur.date_expiration.isoformat() if chauffeur.date_expiration else "",
            "jours_restants": chauffeur.jours_restants(),
        })
    except Chauffeur.DoesNotExist:
        return Response({"error": "Numéro inconnu"}, status=status.HTTP_404_NOT_FOUND)

# --- 5. PROFIL DÉTAILLÉ ---
@api_view(['GET'])
@permission_classes([AllowAny])
def profil_chauffeur(request, pk):
    try:
        chauffeur = Chauffeur.objects.get(pk=pk)
        chauffeur.verifier_statut_abonnement() 
        return Response({
            "id": chauffeur.id,
            "nom": chauffeur.nom,
            "est_actif": chauffeur.est_actif,
            "est_en_ligne": chauffeur.est_en_ligne,
            "date_expiration": chauffeur.date_expiration.isoformat() if chauffeur.date_expiration else "",
            "jours_restants": chauffeur.jours_restants(),
        })
    except Chauffeur.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# --- 6. PAIEMENT PAYTECH ---
@api_view(['GET'])
@permission_classes([AllowAny])
def creer_lien_orange_money(request):
    chauffeur_id = request.query_params.get('chauffeur_id')
    if not chauffeur_id:
        return Response({'error': 'ID manquant'}, status=400)

    # REMPLACE PAR TON URL NGROK ACTUELLE
    BASE_URL = "https://sharika-saxophonic-kendra.ngrok-free.dev"
    
    payload = {
        "item_name": "Abonnement Taxi N'WELE",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": str(uuid.uuid4())[:8],
        "env": "test", 
        "custom_field": json.dumps({"chauffeur_id": chauffeur_id}),
        "success_url": f"{BASE_URL}/api/verifier-statut/{chauffeur_id}/", 
        "cancel_url": f"{BASE_URL}/",
        "ipn_url": f"{BASE_URL}/api/paytech-webhook/"
    }
    headers = {
        "Accept": "application/json", 
        "API_KEY": "4708a871b0d511a24050685ff7abfab2e68c69032e1b3d2913647ef46ed656f2", 
        "API_SECRET": "17cb57b72f679c40ab29eedfcd485bea81582adb770882a78525abfdc57e6784"
    }
    try:
        response = requests.post("https://paytech.sn/api/payment/request-payment", data=payload, headers=headers)
        return Response(response.json())
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# --- 7. WEBHOOK PAYTECH (IPN) ---
@csrf_exempt
@api_view(['POST', 'GET']) # Paytech peut envoyer en POST, on accepte les deux par sécurité
@permission_classes([AllowAny])
def paytech_webhook(request):
    # Les données peuvent arriver dans request.data (POST JSON) ou request.POST (Form-data)
    data_source = request.data if request.data else request.POST
    custom_field = data_source.get('custom_field')

    if custom_field:
        try:
            field_data = json.loads(custom_field)
            chauffeur_id = field_data.get('chauffeur_id')
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            
            # Utilise ta méthode du modèle pour prolonger l'abonnement
            chauffeur.enregistrer_paiement() 
            
            print(f"✅ Paiement IPN validé pour {chauffeur.nom}")
            return Response({"message": "Paiement validé"}, status=200)
        except Exception as e:
            print(f"❌ Erreur Webhook: {e}")
            return Response({"error": "Traitement échoué"}, status=400)
            
    return Response({"error": "Données manquantes"}, status=400)

# --- 8. VÉRIFICATION DU STATUT (Redirection après paiement) ---
@api_view(['GET'])
@permission_classes([AllowAny])
def verifier_statut(request, id):
    try:
        chauffeur = Chauffeur.objects.get(id=id)
        chauffeur.verifier_statut_abonnement() 
        
        # Page simple de confirmation pour le navigateur du téléphone
        html_content = f"""
        <html>
            <body style="text-align:center; font-family:sans-serif; padding-top:50px;">
                <h1 style="color:green;">Paiement Reçu !</h1>
                <p>Merci {chauffeur.nom}, votre compte est maintenant actif.</p>
                <p>Vous pouvez fermer cette page et retourner sur l'application.</p>
                <button onclick="window.close()" style="padding:10px 20px; background:orange; border:none; border-radius:5px;">Retour</button>
            </body>
        </html>
        """
        return HttpResponse(html_content)
    except Chauffeur.DoesNotExist:
        return HttpResponse("Chauffeur introuvable", status=404)

# --- 9. DÉCONNEXION ---
@api_view(['POST'])
def deconnexion_chauffeur(request, pk):
    try:
        chauffeur = Chauffeur.objects.get(pk=pk)
        chauffeur.est_en_ligne = False
        chauffeur.save()
        return Response({'message': 'Déconnecté'}, status=200)
    except Chauffeur.DoesNotExist:
        return Response(status=404)

# --- 10. ENREGISTREMENT MANUEL (INSCRIPTION) ---
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def creer_chauffeur_manuel(request):
    serializer = ChauffeurSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 11. VALIDATION MANUELLE (Pour corriger l'erreur AttributeError) ---
@api_view(['GET'])
@permission_classes([AllowAny])
def valider_paiement_manuel(request, chauffeur_id):
    try:
        chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        # On utilise la méthode de ton modèle pour activer le compte
        chauffeur.enregistrer_paiement() 
        return HttpResponse(f"<h1>Succès</h1><p>Le compte de <b>{chauffeur.nom}</b> a été activé pour 30 jours.</p>")
    except Chauffeur.DoesNotExist:
        return HttpResponse("Erreur : Chauffeur introuvable", status=404)