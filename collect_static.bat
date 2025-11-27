@echo off
REM Collect static files for deployment

echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo Static files collected successfully!
echo Files are in: staticfiles/
pause
