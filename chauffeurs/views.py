import os, requests, time
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.contrib.auth.models import User
from .models import Chauffeur

# --- OUTILS DE REPARATION (URLS DE SECOURS) ---
def force_migrate(request):
    try:
        call_command('migrate', interactive=False)
        return HttpResponse("✅ Migration réussie !")
    except Exception as e:
        return HttpResponse(f"❌ Erreur: {str(e)}")

def creer_admin_force(request):
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@nwele.com', 'Parser1234')
            return HttpResponse("✅ Admin créé (admin / Parser1234)")
        return HttpResponse("ℹ️ L'admin existe déjà.")
    except Exception as e:
        return HttpResponse(f"❌ Erreur: {str(e)}")

# --- API CHAUFFEUR ---
@api_view(['POST'])
@permission_classes([AllowAny])
def connexion_chauffeur(request):
    tel = "".join(filter(str.isdigit, str(request.data.get('telephone', ''))))
    chauffeur = Chauffeur.objects.filter(telephone__icontains=tel).first()
    if chauffeur:
        return Response({
            "id": chauffeur.id,
            "nom_complet": chauffeur.nom_complet,
            "est_actif": chauffeur.est_actif,
            "jours_restants": chauffeur.jours_restants
        })
    return Response({"error": "Chauffeur non trouvé"}, status=404)

@api_view(['POST'])
def mettre_a_jour_chauffeur(request, pk):
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    chauffeur.est_en_ligne = request.data.get('est_en_ligne', chauffeur.est_en_ligne)
    chauffeur.latitude = request.data.get('latitude', chauffeur.latitude)
    chauffeur.longitude = request.data.get('longitude', chauffeur.longitude)
    chauffeur.save()
    return Response({"status": "Mis à jour"})

@api_view(['GET'])
@permission_classes([AllowAny])
def ChauffeurListView(request):
    chauffeurs = Chauffeur.objects.filter(est_actif=True, est_en_ligne=True)
    data = [{"id": c.id, "lat": c.latitude, "lng": c.longitude, "nom": c.nom_complet} for c in chauffeurs]
    return Response(data)

@api_view(['GET'])
def ChauffeurProfilView(request, pk):
    c = get_object_or_404(Chauffeur, pk=pk)
    return Response({"id": c.id, "nom": c.nom_complet, "expire": str(c.date_expiration)})

# --- PAIEMENT ---
@api_view(['POST'])
def PaiementChauffeurView(request, chauffeur_id):
    c = get_object_or_404(Chauffeur, id=chauffeur_id)
    payload = {
        "item_name": "Abonnement N'WELE",
        "item_price": "10000",
        "currency": "XOF",
        "ref_command": f"NWELE-{c.id}-{int(time.time())}",
        "env": "test",
        "ipn_url": "https://nwele-api.onrender.com/api/paiement/callback/",
        "success_url": "https://nwele-api.onrender.com/api/paiement-succes/",
        "cancel_url": "https://nwele-api.onrender.com/api/paiement-succes/",
    }
    headers = {"API_KEY": "4708a871b0d511a24050685ff7abfab2e68c69032e1b3d2913647ef46ed656f2", "API_SECRET": "17cb57b72f679c40ab29eedfcd485bea81582adb770882a78525abfdc57e6784"}
    try:
        r = requests.post("https://paytech.sn/api/payment/request-payment", json=payload, headers=headers)
        return Response(r.json())
    except: return Response({"error": "Paytech injoignable"}, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def PaytechCallbackView(request):
    ref = request.data.get('ref_command')
    if ref and '-' in ref:
        c_id = ref.split('-')[1]
        c = Chauffeur.objects.get(id=c_id)
        c.enregistrer_paiement()
        return Response({"status": "ok"})
    return Response({"status": "error"}, status=400)

def paiement_succes(request):
    return HttpResponse("✅ Paiement terminé !")