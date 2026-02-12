import os, requests, json
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import Chauffeur
from rest_framework import status

# --- CONNEXION ---
@api_view(['POST'])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone', '').strip()
    telephone_clean = "".join(filter(str.isdigit, telephone))
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone_clean)
        return Response({
            "id": chauffeur.id,
            "nom_complet": chauffeur.nom_complet,
            "telephone": chauffeur.telephone,
            "est_actif": chauffeur.est_actif,
            "jours_restants": chauffeur.jours_restants
        })
    except Chauffeur.DoesNotExist:
        return Response({"error": "Chauffeur non trouvé"}, status=404)

# --- MISE À JOUR GPS ---
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
        "jours_restants": chauffeur.jours_restants
    })

# --- PROFIL (CLASSE) ---
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

# --- LISTE POUR LA CARTE (CLASSE) ---
class ChauffeurListView(APIView):
    def get(self, request):
        chauffeurs = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
        data = [{"id": c.id, "nom": c.nom_complet, "lat": c.latitude, "lng": c.longitude} for c in chauffeurs]
        return Response(data)

# --- PAIEMENT ---
@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    # Simulation PayTech (remplace les clés par tes vraies clés)
    payload = {
        "item_name": "Abonnement N'WELE",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": f"PAY-{chauffeur.id}-{os.urandom(2).hex()}",
        "env": "test",
        "ipn_url": "https://nwele-api.onrender.com/api/paiement/callback/",
    }
    # Logique requests.post ici...
    return Response({"url": "https://paytech.sn/payment/checkout/xyz"}) # Exemple

# --- CALLBACK (CLASSE) ---
class PaytechCallbackView(APIView):
    def post(self, request):
        ref_command = request.data.get('ref_command')
        if ref_command:
            try:
                chauffeur_id = ref_command.split('-')[1]
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                chauffeur.enregistrer_paiement()
                return Response({"status": "ok"})
            except: pass
        return Response({"error": "invalid"}, status=400)

# --- UTILITAIRE ---
def creer_admin_force(request):
    from django.contrib.auth.models import User
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@test.com", "admin123")
        return Response("Admin créé")
    return Response("Déjà existant")