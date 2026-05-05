import os
from pathlib import Path

# Chemin de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# SÉCURITÉ : Récupère la clé secrète via l'environnement ou utilise une clé par défaut
SECRET_KEY = os.environ.get('SECRET_KEY', 'nwele-super-secret-key-123')

# IMPORTANT POUR RENDER : DEBUG est False en production
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

# Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Tes applications et extensions
    'chauffeurs',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Gestion des fichiers statiques
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',        # Indispensable pour Flutter
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'taxiprojet.urls'

# --- CONFIGURATION DES TEMPLATES (Correction Erreur admin.E403) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'taxiprojet.wsgi.application'

# --- BASE DE DONNÉES ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- INTERNATIONALISATION ---
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Bamako'
USE_I18N = True
USE_TZ = True

# --- FICHIERS STATIQUES (Whitenoise) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Compression et mise en cache des fichiers statiques
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- FICHIERS MÉDIAS (Photos Voitures/Permis) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- CONFIGURATION CORS & DIVERS ---
CORS_ALLOW_ALL_ORIGINS = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'