# Django settings for timer_app project.

# Not Changing accross computers
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = ()
MANAGERS = ADMINS
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = False
MEDIA_ROOT = ''
MEDIA_URL = ''
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
# Make this unique, and don't share it with anybody.
SECRET_KEY = '+k@(388_pl(c3$*9h&amp;2x=cy3ib24ag!345ihc@3q$jz409*p+n'
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
ROOT_URLCONF = 'production.urls'
WSGI_APPLICATION = 'production.wsgi.application'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django_extensions',
    'boardvision',
    'production',
    'utl_timer',
    'progress_report',
    'manual',
    'tools',
    'supplies',
    'jobhistory'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# unto  this last settings
ACCESS_API_URL = 'http://169.254.184.4/access_api/'

import datetime
d = datetime.datetime.today()
WORKING_DAY_START_HR = 9
WORKING_DAY_START = d.replace(hour=9,minute=0,second=0)
WORKING_DAY_END = d.replace(hour=17,minute=30,second=0)
c = WORKING_DAY_END - WORKING_DAY_START
WORKING_DAY_MINUTES = divmod(c.days * 86400 + c.seconds, 60)[0]

JS_TIME_FORMAT = '%Y/%m/%d %H:%M:%S'

NC_FILES_FOLDER = 'Bigblackbeast\c on big black beast\NCFiles by Models'

# Write folder for Board Vision images
BOARDS_CACHE = 'C:/public_html/img/boards'

# % added to the time per sheet
BOARDS_BREAK = 0

from local_settings import *

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        }
}
