import os

from dotenv import load_dotenv
from pathlib import Path

from config.logging import CustomJsonFormatter

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

CART_SESSION_ID = 'cart'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'django_countries',
    'django_celery_beat',
    'dynamic_breadcrumbs',
    'cachalot',

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
    'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/0",
        'OPTIONS': {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CACHALOT_ENABLED = True
CACHALOT_TIMEOUT = 60 * 60

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

STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

PAYMENT_SUCCESS_URL = os.getenv('PAYMENT_SUCCESS_URL')
PAYMENT_CANCEL_URL = os.getenv('PAYMENT_CANCEL_URL')

AUTH_USER_MODEL = "accounts.CustomUser"
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = []

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CELERY_BROKER_URL = os.getenv('CELERY_BROKER')
CELERY_RESULT_BACKEND = os.getenv('CELERY_BACKEND')

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
        'json': {
            '()': CustomJsonFormatter,
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
            'formatter': 'json',
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
    }
}
