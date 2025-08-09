import os
from pathlib import Path
import ldap
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-bz$n=e+&x44ghl3x7zel-zjyzp9k#neqzz)-7+shnvycv#pj&&'

DEBUG = True

ALLOWED_HOSTS = []

LOGIN_REDIRECT_URL = 'authentication:login_redirect'
LOGIN_URL = 'authentication:login'

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'authentication.apps.AuthenticationConfig',
    'tickets',
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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


from django_auth_ldap.config import LDAPSearch, ActiveDirectoryGroupType

# 1. BACKENDS DE AUTENTICAÇÃO
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# 2. CONFIGURAÇÃO DA CONEXÃO LDAP
AUTH_LDAP_SERVER_URI = os.getenv('LDAP_SERVER_URI'),
AUTH_LDAP_BIND_DN =  os.getenv('BIND_DN')
AUTH_LDAP_BIND_PASSWORD = os.getenv('BIND_PASSWORD')

# Configuração de conexão SSL que funcionou no script de teste
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_X_TLS_NEWCTX: 0,
    ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER
}

# 3. CONFIGURAÇÃO DA BUSCA DE USUÁRIO
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    os.getenv('LDAP_SEARCH_USERS_BASE'),
    ldap.SCOPE_SUBTREE,
    "(sAMAccountName=%(user)s)"
)

# 4. MAPEAMENTO DE ATRIBUTOS E GRUPOS
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# Configuração para dar permissão de acesso ao /admin para teste.
# Pode ser ajustado depois para um grupo específico.
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    
    # Apenas membros deste grupo específico terão acesso ao /admin
    #"is_staff": "CN=STAFF,CN=groups,DC=exemplo,DC=exemplo",
    
    # Você pode fazer o mesmo para superusuários
    #"is_superuser":"CN=ADMIN,OU=groups,DC=exemplo,DC=exemplo",
}

# (Opcional) Se quiser espelhar os grupos do AD para o Django
# Garanta que estas configurações estão ativas para que os grupos funcionem
AUTH_LDAP_MIRROR_GROUPS = True
AUTH_LDAP_FIND_GROUP_PERMS = True

from django_auth_ldap.config import LDAPSearch, ActiveDirectoryGroupType

AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    os.getenv('LDAP_SEARCH_GROUP_BASE'),
    ldap.SCOPE_SUBTREE,
    "(objectClass=group)"
)

# Otimização para grupos do Active Directory
AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType()

AUTH_LDAP_MIRROR_GROUPS_EXCEPT = [
    'Domain Controllers',
    'Domain Admins',
    'Domain Computers',
    'Users',
    'Group Policy Creator Owners',
    'HelpDesk',
]

# 5. CONFIGURAÇÃO DE LOGGING PARA DEPURAÇÃO
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('django_auth_ldap').setLevel(logging.DEBUG)

# CONFIGURAÇÃO DO JAZZMIN

JAZZMIN_SETTINGS = {
    "site_title": "Admin SUDEMA",
    "site_header": "Chamados SUDEMA",
    "site_brand": "Admin SUDEMA",
    "welcome_sign": "Bem-vindo à Administração do Sistema de Chamados SUDEMA",
    "copyright": "SUDEMA",
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index"},
        {"app": "tickets", "name": "Chamados"},
    ],
    "theme": "darkly", # Existem muitos temas, 'darkly' é um tema escuro
}