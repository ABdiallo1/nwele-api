from rest_framework import serializers
from .models import Chauffeur

class ChauffeurSerializer(serializers.ModelSerializer):
    # 'jours_restants' est une @property dans models.py, donc ReadOnlyField
    jours_restants = serializers.ReadOnlyField()
    
    # Utilisation de FileField pour la compatibilité sans Pillow
    photo_permis = serializers.FileField(required=False, allow_null=True)
    photo_voiture = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Chauffeur
        # Liste exacte des champs présents dans ton models.py
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
        # Champs que l'API ne peut pas modifier directement
        read_only_fields = ['id', 'updated_at', 'jours_restants']

    def validate_telephone(self, value):
        """
        Nettoie et valide le numéro de téléphone.
        """
        # Supprime les espaces, tirets et parenthèses
        value = value.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Vérifie si c'est une suite de chiffres (éventuellement avec + au début)
        if not value.isdigit() and not value.startswith('+'):
            raise serializers.ValidationError("Le numéro de téléphone n'est pas valide.")
            
        return value