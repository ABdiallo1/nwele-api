import os, requests, json
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import generics
from .models import Chauffeur
from rest_framework import status

# --- 1. CONNEXION CHAUFFEUR ---
@api_view(['POST'])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone', '').strip()
    if not telephone:
        return Response({"error": "Téléphone requis"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Nettoyage du numéro pour correspondre au format stocké (chiffres uniquement)
    telephone_clean = "".join(filter(str.isdigit, telephone))
    
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone_clean)
        return Response({
            "id": chauffeur.id,
            "nom_complet": chauffeur.nom_complet,
            "telephone": chauffeur.telephone,
            "est_actif": chauffeur.est_actif,
            "jours_restants": chauffeur.jours_restants
        }, status=status.HTTP_200_OK)
    except Chauffeur.DoesNotExist:
        return Response({"error": "Chauffeur non trouvé"}, status=status.HTTP_404_NOT_FOUND)


# --- 2. MISE À JOUR GPS ET STATUT ---
@api_view(['POST', 'PATCH'])
def mettre_a_jour_chauffeur(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    data = request.data
    
    # Mise à jour sélective
    if 'latitude' in data: chauffeur.latitude = data.get('latitude')
    if 'longitude' in data: chauffeur.longitude = data.get('longitude')
    if 'est_en_ligne' in data: chauffeur.est_en_ligne = data.get('est_en_ligne')
    
    chauffeur.save()
    return Response({
        "status": "success",
        "est_actif": chauffeur.est_actif,
        "jours_restants": chauffeur.jours_restants,
        "est_en_ligne": chauffeur.est_en_ligne
    })


# --- 3. PROFIL DÉTAILLÉ (Utilisé par Flutter) ---
class ChauffeurProfilView(APIView):
    def get(self, request, pk):
        chauffeur = get_object_or_404(Chauffeur, pk=pk)
        return Response({
            "id": chauffeur.id,
            "nom_complet": chauffeur.nom_complet,
            "telephone": chauffeur.telephone,
            "est_actif": chauffeur.est_actif,
            "jours_restants": chauffeur.jours_restants,
            "date_expiration": chauffeur.date_expiration,
            "est_en_ligne": chauffeur.est_en_ligne,
            "plaque_immatriculation": chauffeur.plaque_immatriculation
        })


# --- 4. LISTE DES TAXIS ACTIFS (Pour la carte Client) ---
class ChauffeurListView(APIView):
    def get(self, request):
        # On ne montre que les chauffeurs qui ont un abonnement valide ET qui sont en ligne
        chauffeurs = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
        data = []
        for c in chauffeurs:
            data.append({
                "id": c.id,
                "nom": c.nom_complet,
                "lat": c.latitude,
                "lng": c.longitude,
                "telephone": c.telephone
            })
        return Response(data)


# --- 5. INITIALISATION PAIEMENT PAYTECH ---
@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    
    # Configuration PayTech
    # Remplace par tes vraies clés en production
    API_KEY = "ta_cle_api_ici" 
    API_SECRET = "ton_secret_ici"
    
    payload = {
        "item_name": "Abonnement Mensuel N'WELE",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": f"PAY-{chauffeur.id}-{json.dumps(os.urandom(4).hex())}",
        "command_name": f"Abonnement de {chauffeur.nom_complet}",
        "env": "test", # Change en 'live' pour les vrais paiements
        "ipn_url": "https://nwele-api.onrender.com/api/paiement/callback/",
        "success_url": "https://nwele-api.onrender.com/success/",
        "cancel_url": "https://nwele-api.onrender.com/cancel/",
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "API_KEY": API_KEY,
        "API_SECRET": API_SECRET,
    }
    
    try:
        response = requests.post("https://paytech.sn/api/payment/request-payment", json=payload, headers=headers)
        return Response(response.json())
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# --- 6. CALLBACK PAIEMENT (IPN) ---
class PaytechCallbackView(APIView):
    def post(self, request):
        # PayTech envoie les données en POST lors de la validation
        ref_command = request.data.get('ref_command')
        
        if ref_command:
            try:
                # Format de ref_command : PAY-ID-RANDOM
                chauffeur_id = ref_command.split('-')[1]
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                
                # Active l'abonnement via la méthode du modèle
                chauffeur.enregistrer_paiement()
                
                return Response({"status": "Paiement validé avec succès"}, status=200)
            except Exception as e:
                return Response({"error": "Erreur lors du traitement"}, status=400)
        
        return Response({"error": "Données de callback invalides"}, status=400)