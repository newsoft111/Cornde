"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import pymysql
from pathlib import Path
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-_sh@&+rokrvy^1l%751d^5%1xdb4w$7wkibvn#cg1(hrlms4z0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "cornde.com", "www.cornde.com"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
		'django.contrib.sites', 
		'django.contrib.sitemaps',
		'django.contrib.humanize',
		'corsheaders',
		'main',
		'account',
		'gig',
		'util',
		'payment',
		'support',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
								'util.context_processors.check_new_message',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
						'libraries': {
							'campaign_filter': 'gig.templatetags.campaign_filter',
						},
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cornde',
        'USER': 'cornde',
        'PASSWORD': 'ehdwns2510@',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command' : "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}


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

LANGUAGE_CODE = 'ko'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = ( os.path.join('static'), )


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'account.user'
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']

X_FRAME_OPTIONS = "SAMEORIGIN"

EMAIL_HOST = 'smtp.hanmail.net' 		 # 메일 호스트 서버
EMAIL_PORT = 465 			 # 서버 포트
EMAIL_HOST_USER =  'cornde_noreply'
EMAIL_HOST_PASSWORD = 'ehdwns2510123!@#'
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = 'no_reply@cornde.com'	 # 기본 발신자
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]


MAX_UPLOAD_SIZE = 5242880
DATA_UPLOAD_MAX_MEMORY_SIZE = None
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

CURRENT_URL = 'https://cornde.com'
LOGIN_URL = '/account/login/'

CURRENT_BANK = ['기업은행', 
								'국민은행', 
								'우리은행', 
								'신한은행', 
								'하나은행', 
								'농협은행', 
								'지역농축협', 
								'SC제일은행', 
								'한국씨티은행', 
								'우체국', 
								'경남은행', 
								'광주은행', 
								'대구은행', 
								'부산은행',
								'산림조합',
								'산업은행',
								'저축은행',
								'새마을금고',
								'수협',
								'신협',
								'전북은행',
								'제주은행',
								'카카오뱅크',
								'케이뱅크',
								'토스뱅크',
								]