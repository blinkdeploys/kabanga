"""
Django settings for kabanga project.

Generated by 'django-admin startproject' using Django 3.2.17.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
import sys

# sys.modules['fontawesome_free'] = __import__('fontawesome-free')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = os.environ.get('ENV', default='dev')
if env == 'render-staging':
    load_dotenv(BASE_DIR / '.env.render')
elif env == 'architect-staging':
    load_dotenv(BASE_DIR / '.env')
else:
    load_dotenv(BASE_DIR / '.env')
# load_dotenv(BASE_DIR / '.env.docker')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', default='django-insecure-cqwe3w$q)*_bxytqc*36!7%=i0oq#ztunc!f7yd3zea6%#9)ym')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", default=False)

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(' ')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS').split(' ')


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
]
THIRD_PARTY_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_extensions',
    'bootstrap5',
    'fontawesomefree',
    'django_rq',
    'django_redis',
]
kabanga_APPS = [
    'accounts',
    'account',

    '__geo', '__people', '__poll', '__report',

    'kabanga',
    'kabanga.analytics.sales',
    'kabanga.analytics.behavior',
    'kabanga.analytics.inventory_report',
    'kabanga.delivery.partner',
    'kabanga.delivery.tracking',
    'kabanga.misc',
    'kabanga.order.order',
    'kabanga.order.item',
    'kabanga.payment.gateway',
    'kabanga.payment.transaction',
    'kabanga.product.inventory',
    'kabanga.product.product',
    'kabanga.product.rating',
    'kabanga.product.review',
    'kabanga.store.store',
    'kabanga.user.token',
    'kabanga.user.cart',
    'kabanga.user.order_history',
    'kabanga.user.profile',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + kabanga_APPS

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', '0')
REDIS_USER = os.getenv('REDIS_USER')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

RQ_QUEUES = {
    'default': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': REDIS_DB,
        # 'USERNAME': REDIS_USER,
        # 'PASSWORD': REDIS_PASSWORD,
        # 'DEFAULT_TIMEOUT': 360,
        # 'REDIS_CLIENT_KWARGS': {
            # Eventual additional Redis connection arguments
            # 'ssl_cert_reqs': None,
        # },
    },
    # 'with-sentinel': {
        # 'SENTINELS': [('localhost', 26736), ('localhost', 26737)],
        # 'MASTER_NAME': 'redismaster',
        # 'DB': 0,
        # Redis username/password
        # 'USERNAME': 'redis-user',
        # 'PASSWORD': 'secret',
        # 'SOCKET_TIMEOUT': 0.3,
        # 'CONNECTION_KWARGS': {  # Eventual additional Redis connection arguments
            # 'ssl': True
        # },
        # 'SENTINEL_KWARGS': {
            # Eventual Sentinel connection arguments
            # If Sentinel also has auth, username/password can be passed here
            # 'username': 'sentinel-user',
            # 'password': 'secret',
        # },
    # },
    'high': {
        'URL': os.getenv('REDISTOGO_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'), # Heroku
        'DEFAULT_TIMEOUT': 500,
    },
    'low': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': REDIS_DB,
    }
}

# RQ_EXCEPTION_HANDLERS = ['path.to.my.handler']

SESSION_ENGINE = 'django.contrib.sessions.backends.db' 

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'kabanga.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'kabanga.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': POSTGRES_HOST,
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'PORT': POSTGRES_PORT,
    },
    'alt': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
'''
    'default': dj_database_url.parse(os.getenv('POSTGRES_DATABASE_URL')),
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': POSTGRES_HOST,
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'PORT': POSTGRES_PORT,
    },
    'default': dj_database_url.parse(os.getenv('POSTGRES_DATABASE_URL'), conn_max_age=600),
DATABASE_URL = os.getenv('POSTGRES_DATABASE_URL')
    'default': dj_database_url.config(
                                        engine='django.db.backends.postgresql'
                                      ),
'''

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
    os.path.join(os.path.dirname(__file__), '').replace('\\','/'),
]
STATIC_ROOT = BASE_DIR / "staticfiles"


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
    'http://localhost:3001',
)

AUTH_USER_MODEL = "account.User"

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login"

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"

