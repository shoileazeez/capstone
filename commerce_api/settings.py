"""
Django settings for commerce_api project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-mc3c+e@+o8h!fym1u#zo-o+w*9rezk@#^2os6vky$ds+@)&-++'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1', 
    'localhost',  
    'hardeynuga.000.pe',
    'myweb.eu-north-1.elasticbeanstalk.com',
    'ecommerce.eu-north-1.elasticbeanstalk.com',
    'myweb2.eu-north-1.elasticbeanstalk.com',
    'proj.eu-north-1.elasticbeanstalk.com',
    'staging.dntp0v6uhy8vn.amplifyapp.com',
    'capstone-tszo.onrender.com',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'project',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'commerce_api.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'commerce_api.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
}


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'commerce_z8ga',
        'USER': 'hardeynuga',
        'PASSWORD': 'wN1WJ1G5Nl09uTBYw2g62Zlv1OfqCuqh',
        'HOST': 'dpg-cstkeht6l47c73em7h40-a.oregon-postgres.render.com',
        'PORT': '5432'
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True




DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'project.Profile'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
MAILJET_API_KEY = '852682e567c3e6efefd9f068e2055d05'
MAILJET_API_SECRET = '7b9f97f56f018f24b433228ba33738cb'

EMAIL_HOST = 'in-v3.mailjet.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = MAILJET_API_KEY
EMAIL_HOST_PASSWORD = MAILJET_API_SECRET
DEFAULT_FROM_EMAIL = 'shoabdulazeez@gmail.com'


PAYSTACK_SECRET_KEY = 'sk_test_449b06a291136c5a7b507d7c1aa8362b93e7fb5a'
PAYSTACK_PUBLIC_KEY = 'pk_test_79dcbd2bf7ef59e27e5ecc328455c3d3480c8838'
PAYSTACK_BASE_URL = "https://api.paystack.co"
PAYSTACK_CALLBACK_URL = "https://capstone-tszo.onrender.com/payment/callback"
PLATFORM_FEE_PERCENTAGE = 5


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'