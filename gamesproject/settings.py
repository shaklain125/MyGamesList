"""
Django settings for gamesproject project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import socket

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJ_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qfawcrjh2#6(_f&on0+=8d1osm15fd@)p#tl7wt3bbnpd)684m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# ALLOWED_HOSTS = ['127.0.0.1','localhost', str(socket.gethostbyname(socket.gethostname())),'re02.ddns.net']
ALLOWED_HOSTS = ['*']

INTERNAL_IPS = ['127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gamesproject.cron_job_lib.django_crontab',
    'crispy_forms',
    'django.contrib.postgres',
    'mptt',
    'gamesrec',
]

# LOG crons with this , '>> "{0}"'.format(os.path.join(PROJ_DIR, 'cron_jobs.log'))

def mod_second_60(n, f, post_suffix=None):
    # [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30] Accepted N values
    if (60 % n) != 0:
        return []
    s = 0
    c = []
    while s < 60-n:
        s+=n
        if post_suffix != None:
            c.append(('* * * * *',f'prefix_cmd=sleep {s};',f, post_suffix))
        else:
            c.append(('* * * * *',f'prefix_cmd=sleep {s};',f))
    if post_suffix != None:
        c.append(('* * * * *',f, post_suffix))
    else:
        c.append(('* * * * *',f))
    return c


def log_to_file(filename):
    return '>> "{0}"'.format(os.path.join(BASE_DIR, f'logs/{filename}.txt'))

CRONJOBS = [
    ('0 0-23/6 * * *','gamesrec.crons.games_adder',log_to_file('games_adder')), # every 6 hours from 00:00 e.g 00:00, 06:00, 12:00, 18:00
]

CRONJOBS += mod_second_60(10, 'gamesrec.crons.api_status', post_suffix=log_to_file('api_status')) # every 10 seconds

CRONJOBS += ('*/30 * * * *','gamesrec.crons.user_ratings_updater',log_to_file('user_ratings_updater')), # every 30 minutes

CRONJOBS += ('*/5 * * * *','gamesrec.crons.guest_recs_updater',log_to_file('guest_recs_updater')), # every 5 minutes    #mod_second_60(30, 'gamesrec.crons.guest_recs_updater', post_suffix=log_to_file('guest_recs_updater')) # every 30 seconds

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'gamesrec.middleware.theme_middleware',
    'gamesrec.middleware.user_session_middleware',
    'gamesrec.middleware.api_status_middleware',
    'gamesrec.middleware.analytics_middleware',
]

ROOT_URLCONF = 'gamesproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJ_DIR, 'templates')],
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

WSGI_APPLICATION = 'gamesproject.wsgi_windows.application' #'gamesproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# sqlite = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': os.path.join(BASE_DIR, 'db.sqlite3')}

REMOTE_DB = False #SET True if remote database

REMOTE_DB_IP = '' #SET REMOTE DB IP

postgres = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'gamesproj',
    'USER':'admin',
    'PASSWORD':'123456',
    'HOST': 'localhost' if not REMOTE_DB else REMOTE_DB_IP,
    'PORT': '5432',
}

DATABASES = {
    'default': postgres
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USF_FORMAT='usf_datetime'

AUTH_USER_MODEL = 'gamesrec.User'

GEOIP_PATH = os.path.join(PROJ_DIR, 'geoip')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'MyGamesList Team'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'team.mygameslist@gmail.com'
EMAIL_HOST_PASSWORD = 'lugcmqgmqesdupdq'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

PRODUCTION = False

SITE_PATH = '/django/gamesrec'

if not PRODUCTION:
    SITE_PATH = ''; DEBUG = True;
else:
    DEBUG = False

LOGIN_URL = SITE_PATH + '/signin'
LOGIN_REDIRECT_URL = SITE_PATH + '/'

STATIC_URL = SITE_PATH + '/assets/'
MEDIA_URL = SITE_PATH + '/media/'

STATIC_ROOT = os.path.join(PROJ_DIR, "assets")

STATICFILES_DIRS = [
    os.path.join(PROJ_DIR, "static")
]

MEDIA_ROOT = os.path.join(PROJ_DIR, "media")
