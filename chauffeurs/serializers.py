from rest_framework import serializers
from .models import Chauffeur

class ChauffeurSerializer(serializers.ModelSerializer):
    # Utilise la property définie dans le modèle pour calculer les jours
    jours_restants = serializers.ReadOnlyField()

    class Meta:
        model = Chauffeur
        fields = [
            'id', 
            'nom_complet', 
            'telephone', 
            'plaque_immatriculation', 
            'photo_permis', 
            'photo_voiture', 
            'est_actif', 
            'est_en_ligne', 
            'date_expiration', 
            'latitude', 
            'longitude', 
            'jours_restants'
        ]