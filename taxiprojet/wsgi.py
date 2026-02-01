import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxiprojet.settings')

application = get_wsgi_application()

# --- FORCE LA MIGRATION AU DÉMARRAGE ---
from django.core.management import call_command
try:
    print("Exécution des migrations...")
    call_command('migrate', interactive=False)
    print("Migrations terminées avec succès.")
except Exception as e:
    print(f"Erreur lors de la migration : {e}")