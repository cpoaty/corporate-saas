"""
Test settings for accounting_service project.
"""
from .base import *

# Configuration for testing
DEBUG = False
ALLOWED_HOSTS = ['*']

# Use in-memory SQLite database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable password hashing to speed up tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Faster tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Turn off logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# Make tests run faster
DEBUG_PROPAGATE_EXCEPTIONS = True