from rest_framework import serializers
from .models import Chauffeur

class ChauffeurSerializer(serializers.ModelSerializer):
    jours_restants = serializers.ReadOnlyField()
    # On ajoute un champ calculé pour Flutter qui s'appellera toujours 'est_actif'
    # Même si dans ta base le champ s'appelle 'service'
    est_actif = serializers.BooleanField(source='service', read_only=True)

    class Meta:
        model = Chauffeur
        fields = [
            'id', 'nom_complet', 'telephone', 'plaque_immatriculation', 
            'photo_permis', 'photo_voiture', 'est_actif', 'service', 
            'est_en_ligne', 'latitude', 'longitude', 'jours_restants'
        ]
        read_only_fields = ['id', 'jours_restants']