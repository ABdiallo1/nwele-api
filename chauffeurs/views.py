import os, requests, json
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import Chauffeur
from rest_framework import status

# --- 1. CONNEXION ---
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
        return Response({"error": "Chauffeur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

# --- 2. MISE À JOUR GPS ---
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

# --- 3. PROFIL (Classe) ---
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

# --- 4. LISTE TAXIS (Classe) ---
class ChauffeurListView(APIView):
    def get(self, request):
        chauffeurs = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
        data = [{"id": c.id, "nom": c.nom_complet, "lat": c.latitude, "lng": c.longitude} for c in chauffeurs]
        return Response(data)

# --- 5. PAIEMENT ---
@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    # Logique simplifiée pour ne pas bloquer le serveur
    return Response({"url": "https://paytech.sn/payment/checkout/example"})

# --- 6. CALLBACK PAIEMENT (Classe) ---
class PaytechCallbackView(APIView):
    def post(self, request):
        ref_command = request.data.get('ref_command')
        if ref_command:
            try:
                chauffeur_id = ref_command.split('-')[1]
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                chauffeur.enregistrer_paiement()
                return Response({"status": "Success"}, status=200)
            except Exception as e:
                return Response({"error": str(e)}, status=400)
        return Response({"error": "Invalid data"}, status=400)

# --- 7. UTILITAIRE ADMIN ---
def creer_admin_force(request):
    from django.contrib.auth.models import User
    from django.http import HttpResponse
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@test.com", "admin123")
        return HttpResponse("Compte admin créé : admin / admin123")
    return HttpResponse("L'admin existe déjà.")