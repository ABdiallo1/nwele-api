from rest_framework import serializers
from .models import Chauffeur

class ChauffeurSerializer(serializers.ModelSerializer):
    # On précise la source pour être sûr que DRF trouve la méthode dans le modèle
    jours_restants = serializers.ReadOnlyField()
    # Utilise FileField ici aussi
    photo_permis = serializers.FileField(required=False, allow_null=True)
    photo_voiture = serializers.FileField(required=False, allow_null=True)

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
        read_only_fields = ['id', 'updated_at', 'jours_restants']

    # Validation du numéro de téléphone
    def validate_telephone(self, value):
        # Nettoyage des espaces éventuels
        value = value.replace(" ", "")
        if not value.isdigit() and not value.startswith('+'):
            raise serializers.ValidationError("Le numéro de téléphone doit contenir uniquement des chiffres.")
        return value