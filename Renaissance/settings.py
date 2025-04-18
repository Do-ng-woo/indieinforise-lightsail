"""
Django settings for Renaissance project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

from django.urls import reverse, reverse_lazy
from pathlib import Path
import os
from dotenv import load_dotenv


from django.contrib.messages import constants as messages


import environ

env = environ.Env(
    DEBUG=(bool,False)
)

AUTH_USER_MODEL = 'accountapp.CustomUser'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(
    env_file = os.path.join(BASE_DIR, '.env')
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

KAKAO_JS_API_KEY = env('KAKAO_JS_API_KEY')

KAKAO_API_KEY =env('KAKAO_API_KEY')

# SECURITY WARNING: don't run with debug turned on in production!

# DEBUG 설정 (환경 변수에서 읽음)
DEBUG = env('DEBUG')

if DEBUG:  # 로컬 환경
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    ACCOUNT_DEFAULT_HTTP_PROTOCOL='http'
else:  # 서버 환경 (로드밸런서 사용)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True  # HTTP 요청을 HTTPS로 리디렉션
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    ACCOUNT_DEFAULT_HTTP_PROTOCOL='https'

    # 무한 리디렉션 방지를 위한 조건 추가
    if 'HTTP_X_FORWARDED_PROTO' not in os.environ:
        SECURE_SSL_REDIRECT = False

ALLOWED_HOSTS = ['*']



# Application definition

INSTALLED_APPS = [
    'django.contrib.sites',    #allauth 필수
    'allauth',                 #allauth
    'allauth.account',         #allauth
    'allauth.socialaccount',   #allauth
    'allauth.socialaccount.providers.google',  # 구글 로그인 추가
    'allauth.socialaccount.providers.naver',   # 네이버 로그인 추가
    'allauth.socialaccount.providers.kakao',
    'allauth.socialaccount.providers.facebook',
    'accountapp',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap4',
    'profileapp',
    'articleapp',
    'commentapp',
    'projectapp',
    'subscribeapp',
    'artistapp',
    'likeapp',
    'django_select2',
    'personapp',
    'homepageapp',
    'communityapp',
    'tinymce',
    'crispy_forms',
    'crispy_bootstrap4',
    'singapp',
    'albumapp',
    'genreapp',
    'searchapp',
    'instrumentapp',
    'myshowapp',
    'analyticsapp',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
]
# 구글 로그인을 위한 설정
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': '137673191859-6mr8tt40qpgchjqjhmetrbjv2nl3djek.apps.googleusercontent.com',
            'secret': env('GOOGLE_CLIENT_SECRET'),
            'key': ''
        }
    },
    'naver': {
        'SCOPE': ['nickname', 'email'],
        'APP': {
            'client_id': env('NAVER_CLIENT_ID'),
            'secret': env('NAVER_CLIENT_SECRET'),
            'key': ''
        }
    },
    'kakao': {
        'SCOPE': ['account_email','profile_nickname'],
        'APP': {
            'client_id': env('KAKAO_REST_API_KEY'),
            'secret': '',
            'key': ''
        }
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'FIELDS': ['id', 'email', 'name', 'first_name', 'last_name'],
        'VERIFIED_EMAIL': True,
        'VERSION': 'v13.0',  # Facebook API 버전
        'APP': {
            'client_id': env('FACEBOOK_CLIENT_ID'),
            'secret': env('FACEBOOK_CLIENT_SECRET'),
            'key': ''
        }
    }
}



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # allauth의 AccountMiddleware 추가
    'analyticsapp.middleware.VisitorSessionMiddleware',  # VisitorSession 미들웨어 추가
    'accountapp.middleware.ProfileCompletionMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


ROOT_URLCONF = 'Renaissance.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accountapp.context_processors.profile_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'Renaissance.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# 데이터베이스 설정

# 데이터베이스 설정
if DEBUG:  # 로컬 환경
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',  # SQLite 엔진 사용
            'NAME': BASE_DIR / 'db.sqlite3',  # SQLite 파일 경로
        }
    }
else:  # 서버 환경
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',  # MySQL 엔진 사용
            'NAME': env('DB_NAME'),  # 데이터베이스 이름
            'USER': env('DB_USER'),  # 데이터베이스 사용자 이름
            'PASSWORD': env('DB_PASSWORD'),  # 데이터베이스 비밀번호
            'HOST': env('DB_HOST'),  # 데이터베이스 호스트 주소
            'PORT': env('DB_PORT', default='3306'),  # 포트 번호 (기본값 3306)
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES', innodb_strict_mode=1;",
            },
        }
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

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),
                   os.path.join(BASE_DIR, 'staticfiles/django_select2'),]

LOGIN_REDIRECT_URL = reverse_lazy('home')
LOGOUT_REDIRECT_URL = reverse_lazy('home')

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


DATETIME_INPUT_FORMATS = [
    '%Y/%m/%d %H:%M',  # '2024/01/16 18:33' 형식에 맞게 설정
    # 기타 필요한 날짜/시간 형식들을 여기에 추가
]

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

TINYMCE_JS_URL = 'https://cdn.tiny.cloud/1/8dl2747v6qljb2t35lcxsf5a0wae2gegwne1xdzplqf6qmnc/tinymce/5/tinymce.min.js'
TINYMCE_DEFAULT_CONFIG = {
    'height': 360,
    'width': 960,
    'selector': '.tinymce',
    # 추가적인 TinyMCE 설정 옵션을 여기에 추가할 수 있습니
}
CRISPY_TEMPLATE_PACK = 'bootstrap4'  # Bootstrap4를 사용하는 경우

DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000

CSRF_TRUSTED_ORIGINS = [
    'https://www.indieboost.co.kr',
    'https://indieboost.co.kr',
    'http://127.0.0.1:8000'
]

CSRF_COOKIE_SECURE = True

# 이메일 백엔드 설정
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Gmail SMTP 설정
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'indieboostkorea@gmail.com'  # 발신자 이메일 주소
EMAIL_HOST_PASSWORD = env('EMAILPASSWORD')  # 발신자 이메일의 비밀번호 또는 앱 비밀번호

#Celery와 Redis가 같은 서버 내에서 통신하게 되어 설정
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# 세션 만료 시간 (예: 30분)
SESSION_COOKIE_AGE = 1800

# 브라우저 닫아도 세션 유지
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# 세션 저장 방식: 데이터베이스 세션
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SESSION_SAVE_EVERY_REQUEST = True