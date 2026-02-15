from rest_framework import serializers
from .models import Chauffeur

class ChauffeurSerializer(serializers.ModelSerializer):
    # Champ calculé dans le modèle (property)
    jours_restants = serializers.ReadOnlyField()

    class Meta:
        model = Chauffeur
        fields = [
            'id', 
            'nom_complet', 
            'telephone', 
            'plaque_immatriculation', # Assure la visibilité de la plaque
            'photo_permis', 
            'photo_voiture', 
            'est_actif', 
            'est_en_ligne', 
            'date_expiration', 
            'latitude', 
            'longitude', 
            'jours_restants'
        ]

    def get_photo_permis(self, obj):
        """ Retourne l'URL complète de la photo du permis """
        if obj.photo_permis:
            return obj.photo_permis.url
        return None

    def get_photo_voiture(self, obj):
        """ Retourne l'URL complète de la photo de la voiture """
        if obj.photo_voiture:
            return obj.photo_voiture.url
        return None