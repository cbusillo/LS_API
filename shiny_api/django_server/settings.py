"""
For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import locale
from pathlib import Path
import shiny_api.modules.load_config as config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.DJANGO_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'shiny_api.django_server.api.apps',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'shiny_api.django_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'shiny_api.django_server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# #!/usr/bin/env python
# """File to run flask server"""


# app = Flask(__name__)
# app.config['SECRET_KEY'] = config.FLASK_SECRET_KEY
# app.config['WTF_CSRF_TIME_LIMIT'] = None
# app.config["REDIS_URL"] = "redis://localhost"
# app.template_folder = '../views/templates'
# app.debug = False
# running_function: dict = {}

# csrf = CSRFProtect(app)

# app.register_blueprint(sse, url_prefix='/ls_functions')

# toolbar = DebugToolbarExtension(app)


# def flask_url(import_name, url_rules=[], **options):  # pylint: disable=dangerous-default-value
#     """Lazy load a view and add it to the app"""
#     view = LazyView(f"shiny_api.views.{import_name}")
#     for url_rule in url_rules:
#         app.add_url_rule(url_rule, view_func=view, **options)


# flask_url(
#     'ls_functions.ls_functions_view',
#     ['/ls_functions/', '/ls_functions/<module_function_name>'],
#     methods=['GET', 'POST'])
# flask_url('api.workorder_label', ['/api/wo_label/'])
# flask_url('api.ring_central_send_message', ['/api/rc_send_message/'])
# flask_url('label_printer.label_printer_view', [
#     '/label_printer/<active_label_group>',
#     '/label_printer/'], methods=['GET', 'POST'])
# flask_url('table_editor.table_editor_view', [
#     '/table_editor/<active_table>',
#     '/table/'], methods=['GET', 'POST'])


# def start_flask_server():
#     """Start flask server"""
#     webbrowser.open("http://localhost:8000/ls_functions/")
#     app.run(host="0.0.0.0", port=8000)
