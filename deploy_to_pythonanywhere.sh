#!/bin/bash
# Deployment script for PythonAnywhere

echo "🚀 Starting deployment to PythonAnywhere..."

# Navigate to project directory
cd ~/carmannagement

# Pull latest changes from git (if using git)
# git pull origin main

# Install/update requirements
echo "📦 Installing requirements..."
pip install --user -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

echo "✅ Deployment complete!"
echo "⚠️ Don't forget to reload your web app from the PythonAnywhere Web tab!"
echo "🌐 Visit: https://horridhunk254.pythonanywhere.com"
