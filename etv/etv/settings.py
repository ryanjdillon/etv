"""
Django settings for ETV

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
import os
import yamlord

from .env import get_json_path

def get_secret_key():
    from django.utils.crypto import get_random_string
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(50, chars)

PATH_JSON = get_json_path()
FILE_SIMULATIONS = 'simulations'
FILE_SECTIONS = 'parameters'
PATH_CFG_SIM = os.path.join(PATH_JSON, FILE_SIMULATIONS+'.yml')
PATH_CFG_VAR = os.path.join(PATH_JSON, FILE_SECTIONS+'.yml')

# Simulation parameters
SIMULATIONS = yamlord.read_yaml(file_path=PATH_CFG_SIM)
SIM_PARAMS = list(SIMULATIONS[list(SIMULATIONS.keys())[0]].keys())
SECTIONS = yamlord.read_yaml(file_path=PATH_CFG_VAR)

# Output data parameters
# apidata /section/section_parameter/timestep/layer-or-stage
DATA_PARAMS = ['section', 'parameter', 'time_step', 'dimension']


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
try:
    from .secret_key import SECRET_KEY
except ImportError:
    SETTINGS_DIR = os.path.abspath(os.path.dirname(__file__))
    path_secret = os.path.join(SETTINGS_DIR, 'secret_local.py')
    with open(path_secret, 'w') as f:
        f.write("SECRET_KEY = '{}'".format(get_secret_key()))
    from .secret_local import SECRET_KEY

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Application definition
INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'etv_configuration',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.file'
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

ROOT_URLCONF = 'etv.urls'
WSGI_APPLICATION = 'etv.wsgi.application'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

TEST_RUNNER = 'testing.DatabaselessTestRunner'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
# Django prefix for static files
STATIC_URL = '/static/'
STATIC_URL_PREFIX = os.environ.get('STATIC_URL_PREFIX')
if STATIC_URL_PREFIX:
    STATIC_URL = STATIC_URL_PREFIX + STATIC_URL

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
                 #os.path.join(PATH_PROJECT,'plugins')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/
import socket
if socket.gethostname().startswith('symbioses'):
    # on the production server we never want to show
    # debug info
    DEBUG = False
    TEMPLATES[0]['OPTIONS']['debug'] = False
else:
    DEBUG = True
    TEMPLATES[0]['OPTIONS']['debug'] = True

try:
    from .settings_local import *
except:
    pass
