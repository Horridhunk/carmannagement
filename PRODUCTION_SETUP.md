# Production Setup for PythonAnywhere

## Setting DEBUG = False on PythonAnywhere

### Method 1: Using Environment Variable (Recommended)

1. **Open PythonAnywhere Console** and run:
```bash
echo 'export DJANGO_DEBUG=False' >> ~/.bashrc
source ~/.bashrc
```

2. **Or set it in your WSGI file** (`/var/www/horridhunk254_pythonanywhere_com_wsgi.py`):
```python
import os
os.environ['DJANGO_DEBUG'] = 'False'
```

3. **Reload your web app** from the Web tab

### Method 2: Create Production Settings File

1. **Create a production settings file:**
```bash
cd ~/carmannagement/mysystem
nano settings_production.py
```

2. **Add this content:**
```python
from .settings import *

DEBUG = False
```

3. **Update your WSGI file** to use production settings:
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysystem.settings_production')
```

### After Setting DEBUG = False

**Important steps:**

1. **Collect static files:**
```bash
cd ~/carmannagement
python manage.py collectstatic --noinput
```

2. **Reload web app** from PythonAnywhere Web tab

3. **Test your custom error pages:**
   - Visit a non-existent page to see 404 page
   - Custom error pages will now show instead of Django debug pages

### Verify DEBUG Status

Run this in PythonAnywhere console:
```bash
cd ~/carmannagement
python manage.py shell
```

Then:
```python
from django.conf import settings
print(f"DEBUG = {settings.DEBUG}")
```

Should show: `DEBUG = False`

## Current Setup

Your settings.py now automatically detects the environment:
- **Local (Windows)**: DEBUG = True (default)
- **PythonAnywhere**: DEBUG = False (when you set the environment variable)

This means:
- ✅ Easy debugging on your local machine
- ✅ Secure production setup on PythonAnywhere
- ✅ Custom 404/500 pages show in production
- ✅ No need to manually change settings.py

## Troubleshooting

If custom error pages don't show:
1. Verify DEBUG = False
2. Run `python manage.py collectstatic`
3. Reload web app
4. Clear browser cache (Ctrl+Shift+R)


## CSS Cache Busting Setup

The system now includes automatic cache busting for CSS and static files to ensure changes appear immediately.

### How It Works

1. **Context Processor**: `mysystem/context_processors.py` adds a timestamp to all templates
2. **Dynamic Versioning**: CSS files use `?v={{ STATIC_VERSION }}` instead of hardcoded versions
3. **Automatic Updates**: Every server restart generates a new version number

### Benefits

- ✅ No more browser caching issues
- ✅ CSS changes appear immediately after deployment
- ✅ No need to manually update version numbers
- ✅ Works automatically in development and production

### After Deploying CSS Changes

1. **Collect static files:**
```bash
cd ~/carmannagement
python manage.py collectstatic --noinput
```

2. **Reload your web app** from the PythonAnywhere Web tab

3. **Clear browser cache** (optional, but recommended):
   - Chrome/Edge: Ctrl + Shift + Delete
   - Firefox: Ctrl + Shift + Delete
   - Or use hard refresh: Ctrl + F5

### Template Usage

All templates now use dynamic versioning:
```html
<link rel="stylesheet" href="{% static 'clients/styles.css' %}?v={{ STATIC_VERSION }}" />
```

The `STATIC_VERSION` variable is automatically generated on each server restart, ensuring fresh CSS loads.

### Troubleshooting CSS Not Updating

If CSS changes still don't appear:

1. **Check static files are collected:**
```bash
ls -la ~/carmannagement/staticfiles/clients/
```

2. **Verify context processor is enabled** in `settings.py`:
```python
'mysystem.context_processors.static_version',
```

3. **Force reload the web app** from PythonAnywhere Web tab

4. **Check browser console** (F12) for any CSS loading errors
