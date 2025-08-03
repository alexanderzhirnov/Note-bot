import os
from pathlib import Path
from dotenv import load_dotenv
import django

BASE_DIR = Path(__file__).resolve().parent.parent

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notes_project.settings')

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key')


DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['e91bd1749baa.ngrok-free.app', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = [
    'https://e91bd1749baa.ngrok-free.app',
    'https://*.ngrok-free.app'  # Для всех поддоменов ngrok
]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'notes_app.apps.NotesAppConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'notes_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'notes_app.context_processors.telegram_auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'notes_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'notes_db'),
        'USER': os.getenv('POSTGRES_USER', 'user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'pasword'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

AUTH_USER_MODEL = 'notes_app.User'
AUTHENTICATION_BACKENDS = [
    'notes_app.backends.TelegramBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'note_list'
LOGOUT_REDIRECT_URL = 'note_list'
WEBAPP_URL = 'https://567f1d13bde2.ngrok-free.app'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME')
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_BOT_USERNAME:
    raise ValueError("Telegram bot credentials not configured!")

# Настройки для кросс-доменной авторизации
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_HTTPONLY = False  # Для доступа JavaScript
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_DOMAIN = 'e91bd1749baa.ngrok-free.app'  # Ваш домен ngrok
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True