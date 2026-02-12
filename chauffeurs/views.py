import os, requests, json, time
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from .models import Chauffeur

# --- 1. CONNEXION DU CHAUFFEUR ---
@api_view(['POST'])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone', '').strip()
    # On enlève les espaces ou caractères spéciaux du numéro
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


# --- 2. MISE À JOUR GPS ET STATUT EN LIGNE ---
@api_view(['POST', 'PATCH'])
def mettre_a_jour_chauffeur(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    data = request.data
    
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


# --- 3. PROFIL POUR L'APPLICATION (APIView) ---
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
            "est_en_ligne": chauffeur.est_en_ligne
        })


# --- 4. INITIALISATION DU PAIEMENT PAYTECH ---
@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    
    # Remplacer par vos vraies clés PayTech (Paramètres API)
    API_KEY = "VOTRE_API_KEY" 
    API_SECRET = "VOTRE_API_SECRET"
    
    # IMPORTANT: L'URL doit être celle de votre serveur Render
    base_url = "https://nwele-api.onrender.com"
    
    payload = {
        "item_name": "Abonnement Mensuel Taxi N'WELE",
        "item_price": "10000",
        "currency": "XOF",
        # La référence doit être unique à chaque tentative pour éviter l'erreur "Expiré"
        "ref_command": f"PAY-{chauffeur.id}-{int(time.time())}",
        "command_name": f"Paiement chauffeur {chauffeur.nom_complet}",
        "env": "test", # Mettre 'live' quand vous êtes prêt
        "ipn_url": f"{base_url}/api/paiement/callback/",
        "success_url": f"{base_url}/api/profil-chauffeur/{chauffeur.id}/", 
        "cancel_url": f"{base_url}/api/profil-chauffeur/{chauffeur.id}/",
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
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# --- 5. CALLBACK DE VALIDATION (IPN) ---
class PaytechCallbackView(APIView):
    def post(self, request):
        ref_command = request.data.get('ref_command')
        if ref_command:
            try:
                # On extrait l'ID du chauffeur de la ref : PAY-ID-TIMESTAMP
                chauffeur_id = ref_command.split('-')[1]
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                
                # Active l'abonnement dans la base de données
                chauffeur.enregistrer_paiement()
                
                print(f"Paiement validé pour {chauffeur.nom_complet}")
                return Response({"status": "Paiement enregistré"}, status=200)
            except Exception as e:
                return Response({"error": str(e)}, status=400)
        return Response({"error": "Référence manquante"}, status=400)


# --- 6. LISTE DES TAXIS POUR LA CARTE ---
class ChauffeurListView(APIView):
    def get(self, request):
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

# --- 7. COMMANDE DE SECOURS POUR CRÉER UN ADMIN ---
def creer_admin_force(request):
    from django.contrib.auth.models import User
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@nwele.com", "admin123")
        return HttpResponse("Superuser 'admin' créé avec succès.")
    return HttpResponse("L'admin existe déjà.")