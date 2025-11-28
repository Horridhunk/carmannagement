from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .forms import WasherSignupForm
from .models import Washer
from clients.models import Client, PasswordResetToken

def washer_signup_view(request):
    if request.method == 'POST':
        form = WasherSignupForm(request.POST)
        if form.is_valid():
            # Create washer instance from form but don't save yet
            washer = form.save(commit=False)
            # Hash the password and assign to password_hash field
            washer.password_hash = make_password(form.cleaned_data['password'])
            washer.save()
            
            # Automatically log in the washer after account creation
            request.session['washer_id'] = washer.washer_id
            request.session['washer_email'] = washer.email
            request.session['washer_name'] = f"{washer.first_name} {washer.last_name}"
            
            messages.success(request, f'Welcome to your dashboard, {washer.first_name}! Your account has been created successfully.')
            return redirect('washers:dashboard')  # Redirect directly to dashboard
        else:
            # Show specific error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            # Redirect back to auth page with signup form active
            return redirect('washers:auth')
    else:
        form = WasherSignupForm()
    
    return render(request, 'washers/signup.html', {'form': form})

def washer_auth_view(request):
    """Combined login/signup view"""
    return render(request, 'washers/auth.html')

def washer_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Please enter both email and password.')
            return redirect('washers:auth')
        
        try:
            # Query the database for the washer
            washer = Washer.objects.get(email=email)
            
            # Check if the password matches the hashed password in database
            if check_password(password, washer.password_hash):
                # Login successful - store washer info in session
                request.session['washer_id'] = washer.washer_id
                request.session['washer_email'] = washer.email
                request.session['washer_name'] = f"{washer.first_name} {washer.last_name}"
                
                messages.success(request, f'Welcome back, {washer.first_name}!')
                return redirect('washers:dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
                return redirect('washers:auth')
        except Washer.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
            return redirect('washers:auth')
    
    return redirect('washers:auth')

def washer_dashboard_view(request):
    # Check if washer is logged in
    if 'washer_id' not in request.session:
        messages.error(request, 'Please log in to access the dashboard.')
        return redirect('washers:auth')
    
    # Get washer info from session
    washer_id = request.session.get('washer_id')
    washer_name = request.session.get('washer_name', 'Washer')
    
    # Generate initials from washer name
    name_parts = washer_name.split()
    washer_initials = ''.join([part[0].upper() for part in name_parts[:2] if part])
    
    try:
        washer = Washer.objects.get(washer_id=washer_id)
        
        # Get real order data
        from clients.models import WashOrder
        
        # Get current orders assigned to this washer
        current_orders = WashOrder.objects.filter(
            washer=washer,
            status__in=['assigned', 'in_progress']
        ).order_by('-assigned_at')
        
        # Get statistics
        assigned_orders = WashOrder.objects.filter(washer=washer, status='assigned').count()
        in_progress_orders = WashOrder.objects.filter(washer=washer, status='in_progress').count()
        completed_today = WashOrder.objects.filter(
            washer=washer,
            status='completed',
            completed_at__date=timezone.now().date()
        ).count()
        
        context = {
            'washer_name': washer_name,
            'washer_initials': washer_initials,
            'washer_status': washer.status,
            'washer': washer,
            'current_orders': current_orders,
            'assigned_orders': assigned_orders,
            'in_progress_orders': in_progress_orders,
            'completed_today': completed_today,
        }
        
    except Washer.DoesNotExist:
        messages.error(request, 'Washer account not found.')
        return redirect('washers:login')
    
    return render(request, 'washers/dashboard.html', context)

def washer_logout_view(request):
    # Clear the session
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('washers:auth')

def start_wash_view(request, order_id):
    """Start a wash order"""
    if 'washer_id' not in request.session:
        messages.error(request, 'Please log in to access this page.')
        return redirect('washers:auth')
    
    washer_id = request.session.get('washer_id')
    try:
        washer = Washer.objects.get(washer_id=washer_id)
        
        from clients.models import WashOrder
        # Get the order and make sure it's assigned to this washer
        order = WashOrder.objects.get(order_id=order_id, washer=washer, status='assigned')
        
        # Start the wash
        order.status = 'in_progress'
        order.started_at = timezone.now()
        order.save()
        
        messages.success(request, f'Started washing {order.vehicle}!')
        
    except Washer.DoesNotExist:
        messages.error(request, 'Washer account not found.')
        return redirect('washers:auth')
    except WashOrder.DoesNotExist:
        messages.error(request, 'Order not found or not assigned to you.')
    except Exception as e:
        messages.error(request, f'Error starting wash: {str(e)}')
    
    return redirect('washers:dashboard')

def complete_wash_view(request, order_id):
    """Complete a wash order"""
    if 'washer_id' not in request.session:
        messages.error(request, 'Please log in to access this page.')
        return redirect('washers:auth')
    
    washer_id = request.session.get('washer_id')
    try:
        washer = Washer.objects.get(washer_id=washer_id)
        
        from clients.models import WashOrder
        # Get the order and make sure it's assigned to this washer
        order = WashOrder.objects.get(order_id=order_id, washer=washer, status='in_progress')
        
        # Complete the wash
        order.status = 'completed'
        order.completed_at = timezone.now()
        order.save()
        
        # Make washer available again
        washer.is_available = True
        washer.save()
        
        # Send notification to client (optional - can be implemented later)
        messages.success(request, f'Completed washing {order.vehicle}! You are now available for new orders.')
        
    except Washer.DoesNotExist:
        messages.error(request, 'Washer account not found.')
    except WashOrder.DoesNotExist:
        messages.error(request, 'Order not found or not in progress.')
    except Exception as e:
        messages.error(request, f'Error completing wash: {str(e)}')
    
    return redirect('washers:dashboard')

def toggle_availability_view(request):
    """Toggle washer availability status"""
    if 'washer_id' not in request.session:
        messages.error(request, 'Please log in to access this page.')
        return redirect('washers:auth')
    
    washer_id = request.session.get('washer_id')
    try:
        washer = Washer.objects.get(washer_id=washer_id)
        
        # Toggle availability
        washer.is_available = not washer.is_available
        washer.save()
        
        status = "available" if washer.is_available else "unavailable"
        messages.success(request, f'You are now {status} for new orders.')
        
    except Washer.DoesNotExist:
        messages.error(request, 'Washer account not found.')
    except Exception as e:
        messages.error(request, f'Error updating availability: {str(e)}')
    
    return redirect('washers:dashboard')


def washer_profile_view(request):
    """View and edit washer profile"""
    if 'washer_id' not in request.session:
        messages.error(request, 'Please log in to access this page.')
        return redirect('washers:auth')
    
    washer_id = request.session.get('washer_id')
    try:
        washer = Washer.objects.get(washer_id=washer_id)
    except Washer.DoesNotExist:
        messages.error(request, 'Washer account not found.')
        return redirect('washers:auth')
    
    from .forms import WasherProfileForm, WasherPasswordChangeForm
    
    # Initialize forms
    profile_form = WasherProfileForm(instance=washer)
    password_form = WasherPasswordChangeForm(washer=washer)
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = WasherProfileForm(request.POST, instance=washer)
            if profile_form.is_valid():
                profile_form.save()
                # Update session name if changed
                request.session['washer_name'] = f"{washer.first_name} {washer.last_name}"
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('washers:profile')
            else:
                messages.error(request, 'Please correct the errors in the profile form.')
        
        elif 'change_password' in request.POST:
            print(f"=== PASSWORD CHANGE ATTEMPT ===")
            print(f"POST data: {dict(request.POST)}")
            
            # Get form data
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            print(f"Current password provided: {bool(current_password)}")
            print(f"New password provided: {bool(new_password)}")
            print(f"Confirm password provided: {bool(confirm_password)}")
            
            # Manual validation first
            errors = []
            
            if not current_password:
                errors.append("Current password is required.")
            
            if not new_password:
                errors.append("New password is required.")
            
            if not confirm_password:
                errors.append("Please confirm your new password.")
            
            if new_password and len(new_password) < 8:
                errors.append("New password must be at least 8 characters long.")
            
            if new_password and confirm_password and new_password != confirm_password:
                errors.append("New passwords do not match.")
            
            # Check current password
            if current_password:
                from django.contrib.auth.hashers import check_password
                if not check_password(current_password, washer.password_hash):
                    errors.append("Current password is incorrect.")
                    print("Current password verification failed!")
                else:
                    print("Current password verified successfully!")
            
            if errors:
                for error in errors:
                    messages.error(request, error)
                print(f"Validation errors: {errors}")
            else:
                try:
                    from django.contrib.auth.hashers import make_password
                    
                    # Hash and save the new password
                    old_hash = washer.password_hash
                    washer.password_hash = make_password(new_password)
                    washer.save()
                    
                    print(f"Password updated successfully!")
                    print(f"Old hash: {old_hash[:20]}...")
                    print(f"New hash: {washer.password_hash[:20]}...")
                    
                    # Verify the password was saved correctly
                    washer.refresh_from_db()
                    verification = check_password(new_password, washer.password_hash)
                    print(f"Password verification after save: {verification}")
                    
                    messages.success(request, 'Your password has been changed successfully!')
                    return redirect('washers:profile')
                    
                except Exception as e:
                    print(f"Exception during password change: {str(e)}")
                    messages.error(request, f'Error changing password: {str(e)}')
            
            # Reset password form for display
            password_form = WasherPasswordChangeForm(washer=washer)
    
    context = {
        'washer': washer,
        'profile_form': profile_form,
        'password_form': password_form,
        'washer_name': request.session.get('washer_name', 'Washer'),
    }
    
    return render(request, 'washers/profile.html', context)

def debug_password_view(request):
    """Debug view to test password functionality"""
    if 'washer_id' not in request.session:
        return redirect('washers:auth')
    
    washer_id = request.session.get('washer_id')
    try:
        washer = Washer.objects.get(washer_id=washer_id)
        
        if request.method == 'POST':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            
            print(f"Debug password change:")
            print(f"  Current password: {bool(current_password)}")
            print(f"  New password: {bool(new_password)}")
            print(f"  Washer: {washer.email}")
            
            from django.contrib.auth.hashers import check_password, make_password
            
            # Test current password
            current_valid = check_password(current_password, washer.password_hash)
            print(f"  Current password valid: {current_valid}")
            
            if current_valid and new_password:
                # Update password
                old_hash = washer.password_hash
                washer.password_hash = make_password(new_password)
                washer.save()
                
                print(f"  Password saved to database")
                print(f"  Old hash: {old_hash[:20]}...")
                print(f"  New hash: {washer.password_hash[:20]}...")
                
                # Verify it was saved
                washer.refresh_from_db()
                new_valid = check_password(new_password, washer.password_hash)
                print(f"  New password verification: {new_valid}")
                
                return render(request, 'washers/debug_password.html', {
                    'washer': washer,
                    'current_valid': current_valid,
                    'new_valid': new_valid,
                    'success': True,
                    'message': 'Password changed successfully!',
                    'old_hash': old_hash[:20],
                    'new_hash': washer.password_hash[:20]
                })
            else:
                return render(request, 'washers/debug_password.html', {
                    'washer': washer,
                    'current_valid': current_valid,
                    'success': False,
                    'message': 'Current password incorrect or new password empty'
                })
        
        return render(request, 'washers/debug_password.html', {'washer': washer})
        
    except Washer.DoesNotExist:
        return redirect('washers:auth')


def washer_completed_orders_view(request):
    """View completed orders with client reviews"""
    if 'washer_id' not in request.session:
        messages.error(request, 'Please log in to access this page.')
        return redirect('washers:auth')
    
    washer_id = request.session.get('washer_id')
    washer_name = request.session.get('washer_name', 'Washer')
    
    try:
        washer = Washer.objects.get(washer_id=washer_id)
        
        from clients.models import WashOrder, Review
        
        # Get completed orders for this washer
        completed_orders = WashOrder.objects.filter(
            washer=washer,
            status='completed'
        ).select_related('client', 'vehicle').order_by('-completed_at')
        
        # Get reviews for completed orders
        reviews_dict = {}
        for order in completed_orders:
            try:
                review = Review.objects.get(wash_order=order)
                reviews_dict[order.order_id] = review
            except Review.DoesNotExist:
                reviews_dict[order.order_id] = None
        
        context = {
            'washer_name': washer_name,
            'washer': washer,
            'completed_orders': completed_orders,
            'reviews_dict': reviews_dict,
            'total_completed': completed_orders.count(),
        }
        
        return render(request, 'washers/completed_orders.html', context)
        
    except Washer.DoesNotExist:
        messages.error(request, 'Washer account not found.')
        return redirect('washers:login')
