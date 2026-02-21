from rest_framework import serializers
from .models import Chauffeur

class ChauffeurSerializer(serializers.ModelSerializer):
    # On ajoute ces champs pour s'assurer que Flutter reçoive l'URL complète de l'image
    photo_voiture_url = serializers.SerializerMethodField()
    photo_permis_url = serializers.SerializerMethodField()

    class Meta:
        model = Chauffeur
        fields = [
            'id', 'nom_complet', 'telephone', 'plaque_immatriculation', 
            'modele_voiture', 'photo_voiture', 'photo_permis', 
            'photo_voiture_url', 'photo_permis_url',
            'est_actif', 'est_en_ligne', 'latitude', 'longitude'
        ]

    def get_photo_voiture_url(self, obj):
        if obj.photo_voiture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo_voiture.url)
            return obj.photo_voiture.url
        return None

    def get_photo_permis_url(self, obj):
        if obj.photo_permis:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo_permis.url)
            return obj.photo_permis.url
        return None