import os, requests, json
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import Chauffeur

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

class PaytechCallbackView(APIView):
    def post(self, request):
        ref_command = request.data.get('ref_command') # Ex: PAY-5-167...
        if ref_command:
            try:
                # On récupère l'ID du chauffeur stocké dans la référence
                chauffeur_id = ref_command.split('-')[1]
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                
                # UTILISATION DE TA MÉTHODE MODÈLE
                chauffeur.enregistrer_paiement()
                
                print(f"✅ Paiement validé pour {chauffeur.nom_complet}")
                return Response({"status": "Paiement enregistré"}, status=200)
            except Exception as e:
                return Response({"error": str(e)}, status=400)
        return Response({"error": "Référence invalide"}, status=400)

@api_view(['GET'])
def ChauffeurProfilView(request, pk):
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