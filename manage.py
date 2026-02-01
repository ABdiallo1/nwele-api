#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxiprojet.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django n'est pas installé.") from exc
    
    # --- AUTO-CRÉATION ADMIN AMÉLIORÉE ---
    # On vérifie si on est en train de migrer ou de lancer le serveur
    if len(sys.argv) > 1 and sys.argv[1] in ['migrate', 'runserver'] or 'gunicorn' in sys.executable:
        try:
            import django
            django.setup()
            from django.contrib.auth.models import User
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'allassbdiallo.abd@gmail.com', 'Passer1234')
                print("✅ SUCCÈS : Compte Admin créé (admin / Passer1234)")
        except Exception as e:
            # On ignore l'erreur si la base n'est pas encore prête
            pass 
    # -------------------------------------

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()