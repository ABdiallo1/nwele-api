from rest_framework import serializers
from .models import Chauffeur

class ChauffeurSerializer(serializers.ModelSerializer):
    jours_restants = serializers.ReadOnlyField()
    photo_permis = serializers.FileField(required=False, allow_null=True)
    photo_voiture = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Chauffeur
        fields = [
            'id', 'nom_complet', 'telephone', 'plaque_immatriculation', 
            'photo_permis', 'photo_voiture', 'est_actif', 'est_en_ligne', 
            'date_expiration', 'latitude', 'longitude', 'jours_restants', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at', 'jours_restants']