"""
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os

from django.urls import reverse_lazy, reverse
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

CART_SESSION_ID = 'cart'

BACKEND_DOMAIN = "http://localhost"

PAYMENT_SUCCESS_URL = os.getenv('PAYMENT_SUCCESS_URL')
PAYMENT_CANCEL_URL = os.getenv('PAYMENT_CANCEL_URL')

STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

DEBUG = os.getenv('DEBUG', False)

# INTERNAL_IPS = [
# '127.0.0.1',
# 'localhost',
# '172.19.0.4',
# '172.19.0.1',
# '172.19.0.2',
# '172.19.0.6',
# '172.17.0.1'
# '0.0.0.0'
# ]

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'app'
]

if DEBUG:
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]


def custom_show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'django_countries',
    'debug_toolbar',
    'django_celery_beat',
    'dynamic_breadcrumbs',

    'products',
    'accounts',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'orders.context_processors.cart',
                'dynamic_breadcrumbs.context_processors.breadcrumbs',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379",
        'OPTIONS': {
            'db': '1',
        }
    }
}

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://redis:6379/1",
#         "OPTIONS": {
#             "db": "1",
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }


# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

AUTH_USER_MODEL = "accounts.CustomUser"
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = []

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER')
CELERY_RESULT_BACKEND = os.getenv('CELERY_BACKEND')
# CELERY_CACHE_BACKEND = 'default'
# CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# SMTP
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = os.getenv('EMAIL_PORT')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = EMAIL_HOST_USER

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    'formatters': {
        'main': {
            'format': '{asctime} - {levelname} - {module} - {filename} - {message}',
            'style': '{'
        },
        'debug': {
            'format': '{levelname} - {filename} - {message}',
            'style': '{'
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            'formatter': 'main',
        },
        "file": {
            "class": "logging.FileHandler",
            'formatter': 'main',
            'filename': 'info.log',
        },
    },
    "loggers": {
        'main': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'debug': {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        # 'django': {
        #     'handlers': ['file'],
        #     'propagate': True,
        #     'level': 'INFO',
        # },
        # 'django.request': {
        #     'handlers': ['file'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
    }
}
