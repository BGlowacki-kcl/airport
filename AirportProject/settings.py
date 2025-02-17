"""
Django settings for AirportProject project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


import environ
# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['airport-kgl3.onrender.com', '127.0.0.1', 'airport-bglowacki-af4d.d.aivencloud.com']


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    "AI",
    "Analitics",
    "Authentication",
    "Database",
    "Tasks",
    "Users",

    'crispy_forms',
    'crispy_bootstrap4',
    'django_select2',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

AUTH_USER_MODEL = 'Authentication.User'

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "Authentication.middleware.AuthRedirectMiddleware",
    "Users.middleware.UserAccessMiddleware",
    "Users.middleware.UserRedirectMiddleware",
]

ROOT_URLCONF = "AirportProject.urls"

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

WSGI_APPLICATION = "AirportProject.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
import os

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'airport',
#         'USER': 'root',
#         'PASSWORD': env('DB_PASSWORD'),
#         'HOST': 'localhost', #'airport.cnkqmg08gi3q.us-east-1.rds.amazonaws.com',  # or the hostname where your MySQL server is running
#         'PORT': '3306',      # or the port on which your MySQL server is listening
#         # 'OPTIONS': {
#         #     'ssl': {
#         #         #'ca': os.path.join(os.path.dirname(__file__), 'us-east-1-bundle.pem'),  # Path to the RDS CA certificate
#         #         'ca': '/etc/secrets/bundle.pem',  # Path to the RDS CA certificate
#         #     }
#         # }
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'defaultdb',
        'USER': 'avnadmin',
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': 'airport-bglowacki-af4d.d.aivencloud.com',
        'PORT': '19649',      # or the port on which your MySQL server is listening
        'OPTIONS': {
            'ssl': {
                'ca': os.path.join(os.path.dirname(__file__), 'certificate.pem'),  # Path to the RDS CA certificate
                #'ca': '/etc/secrets/bundle.pem',
            }
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = [BASE_DIR / 'static']

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Use a secure backend for sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Use secure cookies if your site uses HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Set the cookie age to something reasonable
SESSION_COOKIE_AGE = 1209600  # 2 weeks, for example

# Ensure HttpOnly flag on cookies to prevent client-side script access
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Optionally, you can enable the secure flag for the CSRF cookie as well
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

CSRF_TRUSTED_ORIGINS = [
    'https://airport-kgl3.onrender.com',  # Replace with your actual Render URL
]
