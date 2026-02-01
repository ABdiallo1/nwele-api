from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Chauffeur
from .serializers import ChauffeurSerializer
import json, requests, uuid

@api_view(['GET'])
@permission_classes([AllowAny])
def liste_taxis(request):
    taxis = Chauffeur.objects.filter(est_en_ligne=True, est_actif=True)
    serializer = ChauffeurSerializer(taxis, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def creer_lien_paytech(request):
    telephone = request.query_params.get('telephone') or request.data.get('telephone')
    try:
        chauffeur = Chauffeur.objects.get(telephone=telephone)
        payload = {
            "item_name": "Abonnement NWELE",
            "item_price": "10000",
            "currency": "XOF",
            "ref_command": f"NW-{uuid.uuid4().hex[:6]}",
            "env": "test",
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
    except Exception as e:
        return Response({'error': 'Chauffeur introuvable'}, status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
def paytech_webhook(request):
    data = request.data
    custom_field = data.get('custom_field')
    if custom_field:
        field = json.loads(custom_field) if isinstance(custom_field, str) else custom_field
        c = Chauffeur.objects.get(id=field.get('chauffeur_id'))
        c.enregistrer_paiement()
        return Response({"status": "SUCCESS"})
    return Response({"status": "FAILED"}, status=400)

@api_view(['GET'])
def verifier_statut(request, id):
    c = Chauffeur.objects.get(id=id)
    return HttpResponse(f"<h1>{c.nom}</h1><p>Statut : {'ACTIF' if c.est_actif else 'INACTIF'}</p>")