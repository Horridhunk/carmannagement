# PythonAnywhere Deployment Guide

This guide will help you deploy your Django car wash management system to PythonAnywhere.

## Prerequisites

1. Create a FREE PythonAnywhere account at https://www.pythonanywhere.com
2. Have your code ready in a Git repository (GitHub, GitLab, or Bitbucket) - optional but recommended
3. That's it! The free tier includes everything you need

## Step 1: Upload Your Code

### Option A: Using Git (Recommended)
1. Open a Bash console on PythonAnywhere
2. Clone your repository:
```bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
```

### Option B: Upload Files
1. Use the "Files" tab to upload your project files
2. Create a directory like `/home/yourusername/mysystem`

## Step 2: Create Virtual Environment

In the PythonAnywhere Bash console:

```bash
# Navigate to your project directory
cd ~/mysystem

# Create virtual environment
mkvirtualenv --python=/usr/bin/python3.10 mysystem-env

# Activate it (should auto-activate after creation)
workon mysystem-env

# Install dependencies
pip install django mysqlclient
```

## Step 3: Configure Database (SQLite - FREE)

Good news! The free tier uses SQLite which is perfect for your car wash system:
- No database setup needed
- Your existing db.sqlite3 works as-is
- Handles multiple users just fine
- Zero configuration required

Simply use SQLite in your settings (see Step 4)

## Step 4: Update Django Settings

Update `mysystem/settings.py` for free tier deployment:

```python
# Add your PythonAnywhere domain to ALLOWED_HOSTS
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com', 'localhost', '127.0.0.1']

# For production, set DEBUG to False (but keep True while testing)
DEBUG = True  # Change to False once everything works

# Generate a new SECRET_KEY (keep it secret!)
SECRET_KEY = 'your-new-secret-key-here'

# SQLite database (FREE TIER)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Step 5: Collect Static Files

In the Bash console:

```bash
cd ~/mysystem
workon mysystem-env
python manage.py collectstatic --noinput
```

## Step 6: Run Migrations

```bash
python manage.py migrate
python manage.py createsuperuser  # Create admin account
```

## Step 7: Configure Web App

1. Go to "Web" tab on PythonAnywhere
2. Click "Add a new web app"
3. Choose "Manual configuration" (not Django wizard)
4. Select Python 3.10

### Configure WSGI File:
1. Click on the WSGI configuration file link
2. Delete all content and replace with:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/mysystem'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysystem.settings'

# Activate virtual environment
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Configure Virtual Environment:
1. In the "Web" tab, find "Virtualenv" section
2. Enter: `/home/yourusername/.virtualenvs/mysystem-env`

### Configure Static Files:
Add these mappings in the "Static files" section:

| URL | Directory |
|-----|-----------|
| /static/ | /home/yourusername/mysystem/staticfiles |

## Step 8: Reload Web App

1. Click the green "Reload" button at the top of the Web tab
2. Visit your site at: `https://yourusername.pythonanywhere.com`

## Step 9: Test Your Application

1. Visit the homepage
2. Test client login at `/`
3. Test admin login at `/carwash-admin/login/`
4. Test washer login at `/washers/login/`

## Troubleshooting

### Check Error Logs:
- Go to "Web" tab
- Click on error log link
- Check for Python errors

### Common Issues:

1. **500 Internal Server Error**
   - Check error log
   - Verify ALLOWED_HOSTS includes your domain
   - Ensure DEBUG = False

2. **Static files not loading**
   - Run `python manage.py collectstatic`
   - Check static files mapping in Web tab
   - Verify STATIC_ROOT in settings.py

3. **Database connection errors**
   - Verify database credentials
   - Check database host name
   - Ensure mysqlclient is installed

4. **Import errors**
   - Verify all dependencies are installed in virtual environment
   - Check sys.path in WSGI file

### Useful Commands:

```bash
# Activate virtual environment
workon mysystem-env

# Update code from Git
cd ~/mysystem
git pull

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

## Security Checklist

- [ ] Set DEBUG = False
- [ ] Generate new SECRET_KEY
- [ ] Add proper ALLOWED_HOSTS
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS (automatic on PythonAnywhere)
- [ ] Set up proper database backups
- [ ] Configure email backend for production

## Updating Your Application

When you make changes:

1. Push changes to Git repository
2. In PythonAnywhere Bash console:
```bash
cd ~/mysystem
git pull
workon mysystem-env
python manage.py migrate  # if database changes
python manage.py collectstatic --noinput  # if static file changes
```
3. Reload web app from Web tab

## Additional Resources

- PythonAnywhere Help: https://help.pythonanywhere.com/
- Django Deployment Checklist: https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/
- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/

## Notes

- Free tier has limitations (daily CPU quota, no custom domains)
- Paid tiers offer MySQL, more CPU, custom domains
- Always test thoroughly after deployment
- Keep your local and production databases separate
