from rest_framework import serializers
from .models import Chauffeur

class ChauffeurSerializer(serializers.ModelSerializer):
    # On ajoute le champ calculé pour Flutter
    jours_restants = serializers.ReadOnlyField()

    class Meta:
        model = Chauffeur
        fields = [
            'id', 'nom', 'telephone', 'plaque_immatriculation', 
            'photo_permis', 'photo_voiture', 'est_actif', 
            'est_en_ligne', 'date_expiration', 'latitude', 
            'longitude', 'jours_restants', 'updated_at'
        ]