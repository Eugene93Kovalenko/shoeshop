from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    'django.shoe-shop.site',
    'shoe-shop.site'
]

CSRF_TRUSTED_ORIGINS = [
    'https://shoe-shop.site',
    'https://django.shoe-shop.site',
]
