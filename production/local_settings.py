DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql_psycopg2',
             'NAME': 'production',
             'USER': 'postgres',
             'PASSWORD': 'ruskin',
             'HOST': '',
             'PORT': ''}}
STATIC_URL = '/static/'
STATICFILES_DIRS = ('/Users/nellobrunelli/Documents/workspace/Python/production/production/static',)
TEMPLATE_DIRS = ('/Users/nellobrunelli/Documents/workspace/Python/production/production/templates',)
HOME_ON_SERVER = ''
SITE_ID = 1

JOBHISTORY_PATH_BRCIKLANE = '/Users/nellobrunelli/Documents/workspace/Python/jobhistory-master/data/JobHistory.xjh'
JOBHISTORY_LINES_BRCIKLANE = 1800

JOBHISTORY_PATH_GARAGE = '/Users/nellobrunelli/Documents/workspace/Python/jobhistory-master/data/JobHistory.xjh'
JOBHISTORY_LINES_GARAGE = 1800

JOBHISTORY_MINIMUM_MINUTES = 1