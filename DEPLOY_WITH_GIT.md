# Git Deployment Workflow for PythonAnywhere

## Your Current Setup
- **Local Development**: Windows machine
- **Version Control**: GitHub repository
- **Production**: PythonAnywhere (pulls from GitHub)

## Deployment Steps

### 1. After Making Changes Locally

```bash
# Check what changed
git status

# Add all changes
git add .

# Commit with a descriptive message
git commit -m "Your change description"

# Push to GitHub
git push origin master
```

### 2. On PythonAnywhere

Open a Bash console and run:

```bash
# Navigate to your project
cd ~/carmannagement

# Pull latest changes from GitHub
git pull origin master

# Install any new requirements (if requirements.txt changed)
pip install --user -r requirements.txt

# Collect static files (IMPORTANT for CSS/JS changes!)
python manage.py collectstatic --noinput

# Run migrations (if models changed)
python manage.py migrate

# Reload the web app
touch /var/www/horridhunk254_pythonanywhere_com_wsgi.py
```

### 3. Reload Web App

Go to the **Web** tab on PythonAnywhere and click the **Reload** button.

## Quick Deployment Script for PythonAnywhere

Save this as `deploy.sh` on PythonAnywhere:

```bash
#!/bin/bash
cd ~/carmannagement
echo "📥 Pulling latest changes..."
git pull origin master
echo "📦 Installing requirements..."
pip install --user -r requirements.txt
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput
echo "🗄️ Running migrations..."
python manage.py migrate
echo "✅ Done! Now reload your web app from the Web tab."
```

Make it executable:
```bash
chmod +x deploy.sh
```

Then just run:
```bash
./deploy.sh
```

## CSS Cache Busting Benefits

With the new cache busting system:
- CSS changes appear immediately after deployment
- No need to manually update version numbers
- Browser cache is automatically bypassed
- Works for all users without them clearing cache

## Common Workflow

### For CSS/Template Changes:
1. Edit files locally
2. Test on local server
3. `git add . && git commit -m "Update CSS/templates" && git push`
4. On PythonAnywhere: `git pull && python manage.py collectstatic --noinput`
5. Reload web app

### For Python Code Changes:
1. Edit files locally
2. Test on local server
3. `git add . && git commit -m "Update views/models" && git push`
4. On PythonAnywhere: `git pull && python manage.py migrate`
5. Reload web app

### For Requirements Changes:
1. Update requirements.txt locally
2. `git add . && git commit -m "Update dependencies" && git push`
3. On PythonAnywhere: `git pull && pip install --user -r requirements.txt`
4. Reload web app

## Troubleshooting

### CSS Not Updating?
1. Did you run `collectstatic`? ✓
2. Did you reload the web app? ✓
3. Hard refresh browser (Ctrl + F5) ✓

### Git Pull Conflicts?
```bash
# Stash local changes
git stash

# Pull from GitHub
git pull origin master

# Reapply your changes
git stash pop
```

### Permission Errors?
```bash
# Make sure you're in the right directory
cd ~/carmannagement

# Check file permissions
ls -la
```

## Best Practices

1. **Always test locally first** before pushing
2. **Write descriptive commit messages**
3. **Pull before you push** to avoid conflicts
4. **Run collectstatic** after CSS/JS changes
5. **Check the error log** if something breaks:
   ```bash
   tail -f /var/www/horridhunk254_pythonanywhere_com_error.log
   ```

## Environment Variables

Remember to set on PythonAnywhere:
```bash
echo 'export DJANGO_DEBUG=False' >> ~/.bashrc
source ~/.bashrc
```

Or in your WSGI file:
```python
os.environ['DJANGO_DEBUG'] = 'False'
```

## Quick Reference

| Action | Local Command | PythonAnywhere Command |
|--------|--------------|------------------------|
| Save changes | `git add . && git commit -m "msg"` | - |
| Deploy | `git push origin master` | `git pull origin master` |
| Static files | `python manage.py collectstatic` | `python manage.py collectstatic --noinput` |
| Database | `python manage.py migrate` | `python manage.py migrate` |
| Restart | Stop/Start server | Reload web app button |

## Your Changes Are Now Live! 🎉

The cache busting system is deployed and will work automatically for all future CSS updates.
