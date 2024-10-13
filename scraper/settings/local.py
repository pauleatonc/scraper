from .base import *
import environ
import os

# Carga las variables de entorno desde .env
# we load the variables from the .env file to the environment
env = environ.Env()
# Especifica la ruta del archivo .env si no está en el directorio raíz
env.read_env(env.str('ENV_PATH', '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-2v0*j0h6p434aq%nj@kv061&4*2jo8$)#is(ul^vv77mrk&6pf'

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("DB_NAME_LOCAL"),
        'USER': os.environ.get("DB_USER_LOCAL"),
        'PASSWORD': os.environ.get("DB_PASSWORD_LOCAL"),
        'HOST': os.environ.get("DB_HOST_LOCAL"),
        'PORT': os.environ.get("DB_PORT_LOCAL"),
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/staticfiles/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
# Defines the base URL and directory to serve user uploaded files during development
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'