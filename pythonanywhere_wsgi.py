"""
WSGI configuration for PythonAnywhere deployment

Copy this content to your WSGI configuration file on PythonAnywhere.
Access it via: Web tab -> WSGI configuration file link

IMPORTANT: Replace 'yourusername' with your actual PythonAnywhere username
"""

import os
import sys

# Add your project directory to the sys.path
# Replace 'yourusername' with your PythonAnywhere username
path = '/home/yourusername/mysystem'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysystem.settings'

# Optional: Use production settings
# os.environ['DJANGO_SETTINGS_MODULE'] = 'mysystem.settings_production'

# Activate virtual environment (PythonAnywhere handles this automatically)
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
