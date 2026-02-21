import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxiprojet.settings')
django.setup()

from chauffeurs.models import Chauffeur

def create_test_chauffeur():
    # Vérifie si le chauffeur existe déjà pour éviter les doublons
    chauffeur, created = Chauffeur.objects.get_or_create(
        telephone="70000000",
        defaults={
            "nom_complet": "Moussa Traoré",
            "plaque_immatriculation": "AM-1234-MD",
            "modele_voiture": "Toyota Corolla",
            "est_actif": False
        }
    )
    if created:
        print("✅ Chauffeur de test créé avec succès !")
    else:
        print("ℹ️ Le chauffeur existe déjà.")

if __name__ == "__main__":
    create_test_chauffeur()