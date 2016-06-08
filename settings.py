import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ALLOWED_HOSTS=['*']

# this is for serving static files with the django development server
import sys
if 'runserver' in sys.argv:
    DEBUG = True
    TEMPLATE_DEBUG = True
else:
    DEBUG = False
    TEMPLATE_DEBUG = False

ADMINS = (
    #(ADMIN_NAME, ADMIN_EMAIL_ADDRESS),
)

EXCEPTION_EMAIL_ADDRESS = '' # for unknown site exceptions
FEEDBACK_EMAIL_ADDRESS = '' # for any user feedback

SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 5 # 60 seconds * 60 minutes * 24 hours * 5 days

EMAIL_USE_TLS = True # assuming gmail
EMAIL_PORT = 587 # assuming gmail
EMAIL_HOST = 'smtp.gmail.com' # assuming gmail
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'session_db/db.sqlite3',
        'OPTIONS':{'timeout':60} # in case database is busy or slow
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# NOTE:vIf running in a Windows environment this must be set to the
#vsame as your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1 # we're number one! we're number one!

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'super-secret-key'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

CACHE_BACKEND = 'locmem:///'

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'urls'

ROOT_PATH = os.path.dirname(__file__)
TEMPLATE_DIRS = (
    os.path.join(ROOT_PATH, 'templates'),
)

INSTALLED_APPS = (
#    'django.contrib.auth',
#    'django.contrib.contenttypes',
    'django.contrib.sessions',
#    'django.contrib.sites',
    'django.contrib.staticfiles',
    'zunzun',
)

# the default JSON serializer yields error in this application
# http://stackoverflow.com/questions/24229397/django-object-is-not-json-serializable-error-after-upgrading-django-to-1-6-5
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

STATIC_URL = '/temp/'

TEMP_FILES_DIR = os.path.join(ROOT_PATH, 'temp')
MAX_TEMP_DIR_SIZE_IN_MBYTES = 500 # default 500 megabytes maximum

STATICFILES_DIRS = (
    TEMP_FILES_DIR,
)
