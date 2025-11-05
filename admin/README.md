# Admin Login System

This admin app provides a secure login system for administrators only. No signup functionality is available - admin accounts must be created manually.

## Features

- **Secure Admin Login**: Only users with `is_staff=True` can access
- **No Signup**: Prevents unauthorized account creation
- **Custom Dashboard**: Clean admin interface
- **Bootstrap Styling**: Professional appearance
- **Management Command**: Easy admin user creation

## URLs

- `/myadmin/login/` - Admin login page
- `/myadmin/dashboard/` - Admin dashboard (requires login)
- `/myadmin/logout/` - Admin logout

## Creating Admin Users

### Method 1: Using Management Command
```bash
python manage.py create_admin <username> <email>
python manage.py create_admin admin admin@example.com --superuser
```

### Method 2: Django Shell
```python
python manage.py shell

from django.contrib.auth.models import User
user = User.objects.create_user('admin', 'admin@example.com', 'password')
user.is_staff = True
user.save()
```

### Method 3: Django Admin Interface
1. Create a superuser: `python manage.py createsuperuser`
2. Login to `/admin/`
3. Create new users and set `is_staff=True`

## Security Features

- Only staff users can login
- Form validation prevents non-admin access
- Session-based authentication
- CSRF protection enabled
- Bootstrap styling with professional appearance

## Templates

- `admin/base.html` - Base template with Bootstrap
- `admin/login.html` - Login form (no signup option)
- `admin/dashboard.html` - Admin dashboard

## Usage

1. Create an admin user using one of the methods above
2. Navigate to `/myadmin/login/`
3. Login with admin credentials
4. Access the dashboard and admin features