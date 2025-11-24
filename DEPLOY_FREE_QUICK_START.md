# Deploy Your Car Wash System FREE - Quick Start

## 5 Simple Steps (15 minutes total)

### Step 1: Sign Up (2 minutes)
1. Go to https://www.pythonanywhere.com
2. Click "Start running Python online in less than a minute!"
3. Create FREE account (no credit card needed)
4. Verify your email

### Step 2: Upload Your Code (3 minutes)

**Option A - If you have Git:**
```bash
# In PythonAnywhere Bash console
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
```

**Option B - No Git:**
1. Zip your project folder on your computer
2. Go to "Files" tab on PythonAnywhere
3. Upload the zip file
4. Unzip it in the console:
```bash
cd ~
unzip yourfile.zip
cd mysystem
```

### Step 3: Setup Environment (5 minutes)

In PythonAnywhere Bash console:

```bash
# Create virtual environment
mkvirtualenv --python=/usr/bin/python3.10 mysystem-env

# Install Django (mysqlclient not needed for SQLite)
pip install django

# Setup database
cd ~/mysystem
python manage.py migrate
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 4: Configure Web App (3 minutes)

1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select "Python 3.10"

**Edit WSGI file:**
Click the WSGI file link and replace everything with:

```python
import os
import sys

# CHANGE 'yourusername' to your actual PythonAnywhere username
path = '/home/yourusername/mysystem'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysystem.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Set Virtual Environment:**
In "Virtualenv" section, enter:
```
/home/yourusername/.virtualenvs/mysystem-env
```

**Add Static Files:**
In "Static files" section, add:
- URL: `/static/`
- Directory: `/home/yourusername/mysystem/staticfiles`

### Step 5: Update Settings & Launch (2 minutes)

Edit `mysystem/settings.py` on PythonAnywhere:

```python
# Find ALLOWED_HOSTS and update it:
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com', 'localhost', '127.0.0.1']

# Make sure DATABASES uses SQLite (should already be set):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Launch:**
1. Click green "Reload" button at top of Web tab
2. Visit: `https://yourusername.pythonanywhere.com`

---

## Done! 🎉

Your car wash system is now live at:
- **Homepage:** https://yourusername.pythonanywhere.com
- **Admin:** https://yourusername.pythonanywhere.com/carwash-admin/login/
- **Washers:** https://yourusername.pythonanywhere.com/washers/login/

---

## Common Issues & Fixes

### "ImportError: No module named django"
```bash
workon mysystem-env
pip install django
```

### "DisallowedHost" error
Add your domain to ALLOWED_HOSTS in settings.py

### Static files not loading
```bash
cd ~/mysystem
workon mysystem-env
python manage.py collectstatic --noinput
```
Then reload web app

### Can't see error details
In settings.py, temporarily set `DEBUG = True` to see errors

---

## Updating Your App Later

When you make changes:

```bash
cd ~/mysystem
git pull  # if using git
workon mysystem-env
python manage.py migrate  # if database changed
python manage.py collectstatic --noinput  # if static files changed
```

Then click "Reload" in Web tab

---

## Free Tier Limits

- ✅ 512MB disk space (plenty for your app)
- ✅ 100MB database (thousands of bookings)
- ✅ One web app (you only need one)
- ✅ HTTPS included
- ⚠️ App sleeps after inactivity (wakes in 2-3 seconds)
- ⚠️ yourusername.pythonanywhere.com domain (custom domain needs paid plan)

**These limits are fine for your car wash system!**

---

## Need Help?

1. Check error log: Web tab → Error log link
2. Check server log: Web tab → Server log link
3. PythonAnywhere forums: https://www.pythonanywhere.com/forums/
4. PythonAnywhere help: https://help.pythonanywhere.com/

---

## When to Upgrade (Later, When You Can Afford It)

Upgrade to $5/month when you need:
- Custom domain (yourcarwash.com)
- MySQL database
- No sleep time
- More storage

But for now, free tier is perfect! 🚀
