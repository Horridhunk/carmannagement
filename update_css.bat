@echo off
REM Quick script to update CSS and restart server

echo ========================================
echo   CSS Update Helper
echo ========================================
echo.

echo Step 1: Collecting static files...
python manage.py collectstatic --noinput
echo.

echo Step 2: Checking for errors...
python manage.py check
echo.

echo ========================================
echo   CSS Update Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Restart your development server (Ctrl+C then run again)
echo 2. Or reload your PythonAnywhere web app
echo 3. Hard refresh your browser (Ctrl + F5)
echo.
pause
