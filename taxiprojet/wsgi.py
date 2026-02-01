import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxiprojet.settings')

application = get_wsgi_application()

# --- CODE D'AUTO-MIGRATION ---
# Ce code s'exécute au démarrage du serveur sur Render
try:
    print("Vérification de la base de données...")
    call_command('migrate', interactive=False)
    print("Base de données à jour.")
except Exception as e:
    print(f"Erreur auto-migrate : {e}")