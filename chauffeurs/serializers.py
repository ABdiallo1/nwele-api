from rest_framework import serializers
from .models import Chauffeur

class ChauffeurSerializer(serializers.ModelSerializer):
    # Ce champ récupère la valeur de la méthode jours_restants() définie dans models.py
    jours_restants = serializers.ReadOnlyField()

    class Meta:
        model = Chauffeur
        fields = [
            'id', 
            'nom', 
            'telephone', 
            'plaque_immatriculation', 
            'photo_permis', 
            'photo_voiture', 
            'est_actif', 
            'est_en_ligne', 
            'date_expiration', 
            'latitude', 
            'longitude', 
            'jours_restants', 
            'updated_at'
        ]

    # Optionnel : Validation pour s'assurer que le numéro de téléphone est au bon format
    def validate_telephone(self, value):
        if not value.isdigit() and not value.startswith('+'):
            raise serializers.ValidationError("Le numéro de téléphone doit contenir uniquement des chiffres.")
        return value