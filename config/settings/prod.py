"""
Production settings for HireHub project.
"""
from .base import *

DEBUG = False

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# Production logging - include file handler
LOGGING['root']['handlers'] = ['console', 'file']

# Ensure ALLOWED_HOSTS is set
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set in production")

# Ensure SECRET_KEY is set and not default
if SECRET_KEY == 'django-insecure-change-this-in-production-1234567890':
    raise ValueError("SECRET_KEY must be changed in production")
