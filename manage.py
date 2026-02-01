#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxiprojet.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # --- SCRIPT D'AUTO-CRÉATION DE L'ADMINISTRATEUR ---
    # Ce bloc s'exécute lors des migrations ou au lancement du serveur
    if len(sys.argv) > 1 and sys.argv[1] in ['migrate', 'runserver'] or 'gunicorn' in sys.argv[0] or 'gunicorn' in sys.executable:
        try:
            import django
            django.setup()
            from django.contrib.auth.models import User
            
            # On vérifie si l'admin existe déjà pour éviter les doublons
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='allassbdiallo.abd@gmail.com',
                    password='Passer1234'
                )
                print("✅ [SYSTÈME] Compte SuperUtilisateur créé avec succès (admin / Passer1234)")
            else:
                print("ℹ️ [SYSTÈME] Le compte Admin existe déjà.")
        except Exception as e:
            # On ne bloque pas le démarrage si la base n'est pas encore prête
            print(f"⚠️ [SYSTÈME] Note : Création admin ignorée (Base de données en cours de préparation...)")
    # --------------------------------------------------

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()