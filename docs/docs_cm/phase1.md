Commencer la Phase 1 avec Anaconda Prompt
1. Créer la documentation et les templates (comme détaillé précédemment)
batchmkdir docs\standards
echo # Standards de développement > docs\standards\development.md
echo. >> docs\standards\development.md
echo ## Conventions de code >> docs\standards\development.md
... (les commandes précédentes pour créer les fichiers de documentation)
2. Initialiser le service d'authentification
batchrem Activer votre environnement Anaconda
conda activate normx_env

rem Se déplacer vers le dossier du service d'authentification
cd core-services\auth-service

rem Installer les dépendances nécessaires avec conda/pip
conda install -c conda-forge django djangorestframework python-dotenv
pip install djangorestframework-simplejwt psycopg2-binary

rem Créer le projet Django
django-admin startproject config src

rem Créer la structure des dossiers
mkdir src\apps
cd src
python manage.py startapp core
move core apps\core

rem Créer les fichiers de configuration
cd ..
mkdir requirements
echo Django>=4.2.7 > requirements\base.txt
echo djangorestframework>=3.14.0 >> requirements\base.txt
echo djangorestframework-simplejwt>=5.3.0 >> requirements\base.txt
echo python-dotenv>=1.0.0 >> requirements\base.txt
echo psycopg2-binary>=2.9.9 >> requirements\base.txt

echo -r base.txt > requirements\development.txt
echo pytest>=7.4.3 >> requirements\development.txt
echo pytest-django>=4.7.0 >> requirements\development.txt
echo black>=23.11.0 >> requirements\development.txt
echo flake8>=6.1.0 >> requirements\development.txt

echo -r base.txt > requirements\production.txt
echo gunicorn>=21.2.0 >> requirements\production.txt

rem Créer un .env pour les variables d'environnement
echo # Environment variables > .env
echo DEBUG=True >> .env
echo SECRET_KEY=your-secret-key-for-development >> .env
echo DATABASE_URL=sqlite:///db.sqlite3 >> .env
3. Configurer le projet Django pour l'authentification
batchrem Créer la structure des fichiers de paramètres
cd src\config
mkdir settings
echo. > settings\__init__.py
echo. > settings\base.py
echo. > settings\development.py
echo. > settings\production.py
Maintenant, modifiez manuellement les fichiers de configuration:

src\config\settings\base.py:

python"""
Base settings for auth-service project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APPS_DIR = BASE_DIR / "apps"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-key-for-dev")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = ["*"]  # Adjust for production

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
]

LOCAL_APPS = [
    "apps.core",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

src\config\settings\development.py:

python"""
Development settings for auth-service project.
"""
from .base import *

DEBUG = True

# CORS settings for development
INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE.insert(1, "corsheaders.middleware.CorsMiddleware")
CORS_ALLOW_ALL_ORIGINS = True  # Only for development!

# Use in-memory cache for development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

src\config\settings\production.py:

python"""
Production settings for auth-service project.
"""
from .base import *

DEBUG = False
ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOSTS", "").split(",")]

# Security settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Use Redis cache for production
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://redis:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Database settings for production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "auth_service"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "postgres"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

Mettre à jour src\config\settings\__init__.py:

python"""
Settings module.
Default to development settings.
"""
import os

environment = os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.development")

if environment == "config.settings.production":
    from .production import *
else:
    from .development import *

Mettre à jour src\config\urls.py:

python"""
URL configuration for auth-service project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # JWT endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Core API
    path("api/", include("apps.core.urls")),
]
4. Créer l'application core avec modèles utilisateur

Créer le fichier src\apps\core\urls.py:

python"""
Core app URLs.
"""
from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
]

Créer le fichier src\apps\core\views.py:

python"""
Core app views.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Basic health check endpoint.
    """
    return Response({"status": "ok"})
5. Rendre le projet exécutable

Modifier le fichier src\manage.py pour utiliser les nouveaux paramètres:

python#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
        
    # Add the parent directory to sys.path for better imports
    current_path = Path(__file__).parent.resolve()
    sys.path.append(str(current_path))
    
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
6. Tester le service
batchrem Revenir au dossier du service
cd C:\Users\chris\corporate-saas\core-services\auth-service\src

rem Migrer la base de données
python manage.py migrate

rem Créer un utilisateur admin
python manage.py createsuperuser

rem Lancer le serveur
python manage.py runserver
Maintenant, vous pouvez accéder à:

http://127.0.0.1:8000/admin/ - pour l'interface d'administration
http://127.0.0.1:8000/api/health/ - pour vérifier que l'API fonctionne
http://127.0.0.1:8000/api/token/ - pour l'endpoint d'authentification JWT

7. Committer le service d'authentification
batchcd C:\Users\chris\corporate-saas
git add core-services\auth-service
git commit -m "Initialisation du service d'authentification"
git push