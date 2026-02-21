#!/usr/bin/env bash
# Arrêter le script en cas d'erreur
set -o errexit

# Installer les dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques (CSS/JS)
python manage.py collectstatic --noinput

# Appliquer les migrations à la base de données
python manage.py migrate