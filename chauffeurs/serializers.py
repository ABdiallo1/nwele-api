from rest_framework import serializers
from .models import Chauffeur

class ChauffeurSerializer(serializers.ModelSerializer):
    # Champ calculé pour informer le chauffeur sur Flutter
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
            'est_actif',        # Correspond au statut de l'abonnement
            'est_en_ligne',     # Correspond au statut du Switch dans le Dashboard
            'date_expiration', 
            'latitude', 
            'longitude', 
            'jours_restants'
        ]

    def validate_telephone(self, value):
        """Nettoie le numéro de téléphone avant validation"""
        cleaned_number = "".join(filter(str.isdigit, str(value)))
        if len(cleaned_number) < 8:
            raise serializers.ValidationError("Le numéro de téléphone est trop court.")
        return cleaned_number