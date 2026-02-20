import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURATION MEDIA (IMAGES) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- CONFIGURATION FEDAPAY ---
# Lit la clé depuis Render, sinon utilise la sandbox par défaut
FEDAPAY_API_KEY = os.environ.get('FEDAPAY_API_KEY', 'sk_sandbox_JVBu9SjQL5rl3Ka4_muQ0J4h')

# Assurez-vous d'ajouter 'chauffeurs' dans INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chauffeurs', 
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Doit être en haut
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Pour les fichiers statiques sur Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True # Autorise Flutter à communiquer avec Django