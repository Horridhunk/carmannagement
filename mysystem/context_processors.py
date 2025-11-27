"""
Context processors for the mysystem project.
"""
import time

def static_version(request):
    """
    Add a static version timestamp to all templates for cache busting.
    This ensures CSS and JS files are reloaded when changes are made.
    """
    return {
        'STATIC_VERSION': str(int(time.time()))
    }
