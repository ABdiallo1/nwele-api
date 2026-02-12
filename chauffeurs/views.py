import os, requests, json, time
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Chauffeur

@api_view(['POST'])
def connexion_chauffeur(request):
    telephone = request.data.get('telephone', '').strip()
    telephone_clean = "".join(filter(str.isdigit, telephone))
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone_clean)
        return Response({
            "id": chauffeur.id,
            "nom_complet": chauffeur.nom_complet,
            "est_actif": chauffeur.est_actif,
            "jours_restants": chauffeur.jours_restants
        })
    except:
        return Response({"error": "Chauffeur non trouvé"}, status=404)

@api_view(['GET'])
def ChauffeurProfilView(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    return Response({
        "id": chauffeur.id,
        "nom_complet": chauffeur.nom_complet,
        "est_actif": chauffeur.est_actif,
        "jours_restants": chauffeur.jours_restants,
        "date_expiration": str(chauffeur.date_expiration)
    })

@api_view(['POST', 'PATCH'])
def mettre_a_jour_chauffeur(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    data = request.data
    if 'latitude' in data: chauffeur.latitude = data.get('latitude')
    if 'longitude' in data: chauffeur.longitude = data.get('longitude')
    if 'est_en_ligne' in data: chauffeur.est_en_ligne = data.get('est_en_ligne')
    chauffeur.save()
    return Response({"status": "success"})

@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    # Remplacer par tes clés PayTech
    headers = {"API_KEY": "TON_API_KEY", "API_SECRET": "TON_API_SECRET"}
    payload = {
        "item_name": "Abonnement N'WELE",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": f"PAY-{chauffeur.id}-{int(time.time())}",
        "env": "test",
        "success_url": f"https://nwele-api.onrender.com/api/profil-chauffeur/{chauffeur.id}/",
        "ipn_url": "https://nwele-api.onrender.com/api/paiement/callback/",
    }
    try:
        r = requests.post("https://paytech.sn/api/payment/request-payment", json=payload, headers=headers)
        return Response(r.json())
    except:
        return Response({"error": "Erreur PayTech"}, status=400)

@api_view(['POST'])
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

@api_view(['GET'])
def ChauffeurListView(request):
    chauffeurs = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    data = [{"id": c.id, "lat": c.latitude, "lng": c.longitude} for c in chauffeurs]
    return Response(data)

def creer_admin_force(request):
    from django.contrib.auth.models import User
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@test.com", "admin123")
        return HttpResponse("Admin créé")
    return HttpResponse("Admin existe déjà")