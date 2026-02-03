from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-votre-cle-ici')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True 

ALLOWED_HOSTS = ['*', 'nwele-api.onrender.com', 'localhost', '127.0.0.1']

# Sécurité pour les formulaires et les requêtes API sur Render
CSRF_TRUSTED_ORIGINS = ['https://nwele-api.onrender.com']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # Pour servir les fichiers statiques en dev
    'django.contrib.staticfiles',
    
    # Bibliothèques tierces
    'rest_framework',
    'corsheaders',
    
    # Tes applications
    'chauffeurs',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Doit être juste après SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Doit être avant CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'taxiprojet.urls'

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
                'django.template.context_processors.media', # Indispensable pour voir les images dans l'admin
            ],
        },
    },
]

WSGI_APPLICATION = 'taxiprojet.wsgi.application'

# Database
# Note : SQLite sur Render est réinitialisé à chaque déploiement.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Bamako' # Mis à jour pour le Mali
USE_I18N = True
USE_TZ = True

# --- CONFIGURATION DES FICHIERS STATIQUES (CSS, JS) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Whitenoise pour servir les fichiers statiques sur Render
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- CONFIGURATION DES MÉDIAS (PHOTOS) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Créer automatiquement le dossier media s'il n'existe pas localement
if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)

# --- CONFIGURATION CORS ---
CORS_ALLOW_ALL_ORIGINS = True # Permet à l'app Flutter de communiquer librement
CORS_ALLOW_CREDENTIALS = True

# --- RÉGLAGES SUPPLÉMENTAIRES ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Force Django à ajouter le slash final pour éviter les erreurs 301 avec Flutter
APPEND_SLASH = True