from rest_framework import serializers
from .models import Chauffeur

class ChauffeurSerializer(serializers.ModelSerializer):
    # On ajoute jours_restants comme un champ calculé (provenant du @property du modèle)
    jours_restants = serializers.ReadOnlyField()

    class Meta:
        model = Chauffeur
        # On liste explicitement tous les champs dont Flutter a besoin
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
            'jours_restants',
            'latitude', 
            'longitude'
        ]

    def get_photo_permis(self, obj):
        """ Retourne l'URL complète de l'image pour éviter les erreurs d'affichage """
        if obj.photo_permis and hasattr(obj.photo_permis, 'url'):
            return obj.photo_permis.url
        return None

    def get_photo_voiture(self, obj):
        if obj.photo_voiture and hasattr(obj.photo_voiture, 'url'):
            return obj.photo_voiture.url
        return None