"""
Production settings for PythonAnywhere deployment
Import this in your WSGI file or use environment variable
"""
from .settings import *

# SECURITY WARNING: Change this in production!
SECRET_KEY = 'CHANGE-THIS-TO-A-RANDOM-SECRET-KEY-IN-PRODUCTION'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Update with your PythonAnywhere username
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com', 'localhost', '127.0.0.1']

# Database configuration for PythonAnywhere MySQL (paid tier)
# Update with your actual credentials
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yourusername$systemusers',
        'USER': 'yourusername',
        'PASSWORD': 'your-mysql-password',
        'HOST': 'yourusername.mysql.pythonanywhere-services.com',
        'PORT': '3306',
    }
}

# For free tier using SQLite, uncomment this instead:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Email configuration for production
# Configure with your actual SMTP settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Car Wash System <your-email@gmail.com>'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
