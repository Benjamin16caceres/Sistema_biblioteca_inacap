import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Configurar django-environ
env = environ.Env()

# LEER .env DESDE LA CARPETA BASE
env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='clave-temporal-para-pruebas')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'biblioteca_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'biblioteca_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# CONFIGURACIÓN DE BASE DE DATOS MÁS SIMPLE
# REEMPLAZA tu configuración actual con esta:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': f'{env("DB_HOST")}:{env("DB_PORT")}/{env("DB_NAME")}',
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
    }
}

# O si prefieres usar variables env, cambia esta parte:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.oracle',
#         'NAME': f'{env("DB_HOST", default="192.168.1.86")}:{env("DB_PORT", default="1521")}/{env("DB_NAME", default="xepdb1")}',
#         'USER': env('DB_USER', default='system'),
#         'PASSWORD': env('PASSWORD', default='oracle'),  # Cambiado de DB_PASSWORD a PASSWORD
#     }
# }

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'