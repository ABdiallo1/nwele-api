from rest_framework import serializers
from .models import Chauffeur

class ChauffeurSerializer(serializers.ModelSerializer):
    # jours_restants est calculé dynamiquement dans le modèle
    jours_restants = serializers.ReadOnlyField()
    
    # FileField permet de gérer les images sans la bibliothèque Pillow si nécessaire
    photo_permis = serializers.FileField(required=False, allow_null=True)
    photo_voiture = serializers.FileField(required=False, allow_null=True)

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
            'jours_restants', 
            'updated_at'
        ]
        read_only_fields = ['id', 'updated_at', 'jours_restants']

    def validate_telephone(self, value):
        """ Nettoyage du numéro : supprime les caractères spéciaux """
        if value:
            value = value.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            
            if not value.isdigit() and not value.startswith('+'):
                raise serializers.ValidationError("Le numéro de téléphone n'est pas valide.")
        return value