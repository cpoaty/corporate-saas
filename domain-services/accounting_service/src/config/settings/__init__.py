"""
Settings loader for accounting_service project.
"""
import os

# Déterminer quel fichier de paramètres utiliser
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *
elif environment == 'test':
    from .test import *
else:
    from .development import *