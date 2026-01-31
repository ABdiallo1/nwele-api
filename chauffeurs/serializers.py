from rest_framework import serializers
from .models import Chauffeur
from django.utils import timezone

class ChauffeurSerializer(serializers.ModelSerializer):
    # Champ calculé pour afficher le nombre de jours restants
    jours_restants = serializers.SerializerMethodField()

    class Meta:
        model = Chauffeur
        # On inclut TOUS les champs nécessaires :
        # - Pour le passager (nom, tel, position)
        # - Pour ton enregistrement (photo_permis, photo_voiture, plaque)
        fields = [
            'id', 'nom', 'nom_complet', 'telephone', 'plaque_immatriculation',
            'photo_permis', 'photo_voiture', 
            'est_en_ligne', 'est_actif', 'date_expiration', 
            'latitude', 'longitude', 'jours_restants'
        ]
        
        # Sécurité : On rend ces champs optionnels pour ne pas bloquer 
        # la mise à jour GPS si la photo n'est pas envoyée
        extra_kwargs = {
            'photo_permis': {'required': False},
            'photo_voiture': {'required': False},
        }

    def get_jours_restants(self, obj):
        """Calcule dynamiquement les jours restants avant expiration"""
        if obj.date_expiration:
            maintenant = timezone.now()
            if obj.date_expiration > maintenant:
                delta = obj.date_expiration - maintenant
                return delta.days
        return 0