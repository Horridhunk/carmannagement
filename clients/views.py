from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .forms import SignupForm, ForgotPasswordForm, ResetPasswordForm, VehicleForm, WashOrderForm, AppointmentForm, TimeSlotSelectionForm
from .models import Client, PasswordResetToken, Vehicle, WashOrder, Appointment, TimeSlot
from django.db import models

def clients(request):
  template = loader.get_template('myfirst.html')
  return HttpResponse(template.render())

# ... other imports
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                # Create client instance from form but don't save yet
                client = form.save(commit=False)
                # Hash the password and assign to password_hash field
                client.password_hash = make_password(form.cleaned_data['password'])
                client.save()
                
                # Automatically log in the user after account creation
                request.session['client_id'] = client.client_id
                request.session['client_email'] = client.email
                request.session['client_name'] = f"{client.first_name} {client.last_name}"
                
                messages.success(request, f'Welcome to your dashboard, {client.first_name}! Your account has been created successfully.')
                return redirect('clients:dashboard')
            except Exception as e:
                messages.error(request, f'An error occurred while creating your account. Please try again.')
                print(f"Signup error: {e}")  # For debugging
        else:
            # Display specific form errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_name = form.fields[field].label or field.replace('_', ' ').title()
                        messages.error(request, f"{field_name}: {error}")
    else:
        form = SignupForm()
    
    return render(request, 'clients/login.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Please enter both email and password.')
            return render(request, 'clients/login.html')
        
        try:
            # Query your database for the client
            client = Client.objects.get(email=email)
            
            # Check if the password matches the hashed password in database
            if check_password(password, client.password_hash):
                # Login successful - store user info in session
                request.session['client_id'] = client.client_id
                request.session['client_email'] = client.email
                request.session['client_name'] = f"{client.first_name} {client.last_name}"
                request.session['is_guest'] = False
                
                messages.success(request, f'Welcome back, {client.first_name}!')
                return redirect('clients:dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        except Client.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'clients/login.html')

def guest_login_view(request):
    """Allow users to browse as guest without creating an account"""
    # Set guest session data
    request.session['client_id'] = 'guest'
    request.session['client_email'] = 'guest@carwash.com'
    request.session['client_name'] = 'Guest User'
    request.session['is_guest'] = True
    
    messages.info(request, 'You are browsing as a guest. Sign up to book services and track orders.')
    return redirect('clients:dashboard')

def dashboard_view(request):
    # Check if user is logged in
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to access the dashboard.')
        return redirect('clients:login')
    
    # Get client info from session
    client_id = request.session.get('client_id')
    client_name = request.session.get('client_name', 'User')
    client_email = request.session.get('client_email', '')
    is_guest = request.session.get('is_guest', False)
    
    # Generate initials from client name
    name_parts = client_name.split()
    client_initials = ''.join([part[0].upper() for part in name_parts[:2] if part])
    
    # Initialize default values
    total_orders = 0
    total_cars = 0
    pending_orders = 0
    total_spent = 0
    recent_orders = []
    client_reviews = []
    
    # If guest mode, show demo data
    if is_guest:
        context = {
            'client_name': client_name,
            'client_initials': client_initials,
            'client_email': client_email,
            'is_guest': True,
            'total_orders': 0,
            'total_cars': 0,
            'pending_orders': 0,
            'total_spent': 0,
            'recent_orders': [],
            'client_reviews': [],
        }
        return render(request, 'clients/dashboard.html', context)
    
    try:
        # Get client object
        client = Client.objects.get(client_id=client_id)
        
        # Get vehicle count
        try:
            total_cars = Vehicle.objects.filter(client=client).count()
        except Exception:
            pass
        
        # Try to get order data if tables exist
        try:
            total_orders = WashOrder.objects.filter(client=client).count()
            pending_orders = WashOrder.objects.filter(client=client, status='pending').count()
            recent_orders = WashOrder.objects.filter(client=client).order_by('-created_at')[:5]
            
            # Calculate total spent
            completed_orders = WashOrder.objects.filter(client=client, status='completed')
            total_spent = sum(order.price for order in completed_orders)
        except Exception:
            pass
        
        # Get client reviews
        try:
            from .models import Review
            client_reviews = Review.objects.filter(client=client).select_related('wash_order', 'washer').order_by('-created_at')[:3]
        except Exception:
            pass
            
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')
    
    context = {
        'client_name': client_name,
        'client_initials': client_initials,
        'client_email': client_email,
        'is_guest': is_guest,
        'total_orders': total_orders,
        'total_cars': total_cars,
        'pending_orders': pending_orders,
        'total_spent': total_spent,
        'recent_orders': recent_orders,
        'client_reviews': client_reviews,
    }
    
    return render(request, 'clients/dashboard.html', context)

def logout_view(request):
    # Clear the session
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('clients:login')
def index_view(request):
    return render(request, 'clients/index.html')

def home_view(request):
    """Landing page with all system links"""
    return render(request, 'clients/home.html')

def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                client = Client.objects.get(email=email)
                
                # Invalidate any existing tokens for this client
                PasswordResetToken.objects.filter(client=client, is_used=False).update(is_used=True)
                
                # Create new password reset token
                reset_token = PasswordResetToken.objects.create(client=client)
                
                # Build reset URL
                reset_url = request.build_absolute_uri(
                    reverse('clients:reset_password', kwargs={'token': reset_token.token})
                )
                
                # Send email with HTML template
                try:
                    from django.template.loader import render_to_string
                    from django.utils.html import strip_tags
                    
                    # Create HTML email content
                    html_message = render_to_string('clients/emails/password_reset.html', {
                        'client': client,
                        'reset_url': reset_url,
                        'site_name': 'Car Wash Management System'
                    })
                    plain_message = strip_tags(html_message)
                    
                    send_mail(
                        subject='Password Reset Request - Car Wash System',
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    messages.success(request, 
                        'Password reset instructions have been sent to your email address. '
                        'Please check your inbox and follow the instructions to reset your password.'
                    )
                except Exception as e:
                    # For development, show the reset link in the message
                    messages.success(request, 
                        f'Development Mode: Password reset link: {reset_url}\n'
                        f'(In production, this would be sent to your email: {email})'
                    )
                    
            except Client.DoesNotExist:
                # For security, don't reveal if email exists or not
                messages.success(request, 
                    'If an account with that email exists, password reset instructions have been sent.'
                )
            
            return redirect('clients:forgot_password')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'clients/forgot_password.html', {'form': form})

def reset_password_view(request, token):
    reset_token = get_object_or_404(PasswordResetToken, token=token)
    
    if not reset_token.is_valid():
        messages.error(request, 'This password reset link has expired or is invalid.')
        return redirect('clients:forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            
            # Update client password
            client = reset_token.client
            client.password_hash = make_password(new_password)
            client.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            messages.success(request, 'Your password has been reset successfully. You can now log in.')
            return redirect('clients:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'clients/reset_password.html', {'form': form, 'token': token})

def manage_vehicles_view(request):
    """View to manage client's vehicles"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to access this page.')
        return redirect('clients:login')
    
    # Check if guest mode
    if request.session.get('is_guest', False):
        messages.warning(request, 'Please sign up or log in to manage vehicles.')
        return redirect('clients:signup')
    
    client_id = request.session.get('client_id')
    try:
        client = Client.objects.get(client_id=client_id)
        vehicles = Vehicle.objects.filter(client=client).order_by('-date_added')
        
        context = {
            'client_name': request.session.get('client_name', 'User'),
            'vehicles': vehicles,
        }
        return render(request, 'clients/manage_vehicles.html', context)
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')

def add_vehicle_view(request):
    """Add a new vehicle"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to access this page.')
        return redirect('clients:login')
    
    # Check if guest mode
    if request.session.get('is_guest', False):
        messages.warning(request, 'Please sign up or log in to add vehicles.')
        return redirect('clients:signup')
    
    client_id = request.session.get('client_id')
    try:
        client = Client.objects.get(client_id=client_id)
        
        if request.method == 'POST':
            form = VehicleForm(request.POST)
            if form.is_valid():
                vehicle = form.save(commit=False)
                vehicle.client = client
                vehicle.save()
                messages.success(request, f'Vehicle {vehicle} has been added successfully!')
                return redirect('clients:manage_vehicles')
        else:
            form = VehicleForm()
        
        context = {
            'client_name': request.session.get('client_name', 'User'),
            'form': form,
            'title': 'Add New Vehicle'
        }
        return render(request, 'clients/add_vehicle.html', context)
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')

def book_wash_view(request):
    """Book a new wash order"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to access this page.')
        return redirect('clients:login')
    
    # Check if guest mode
    if request.session.get('is_guest', False):
        messages.warning(request, 'Please sign up or log in to book a wash service.')
        return redirect('clients:signup')
    
    client_id = request.session.get('client_id')
    try:
        client = Client.objects.get(client_id=client_id)
        
        # Check if client has any vehicles
        if not Vehicle.objects.filter(client=client).exists():
            messages.error(request, 'Please add a vehicle first before booking a wash.')
            return redirect('clients:add_vehicle')
        
        if request.method == 'POST':
            form = WashOrderForm(client=client, data=request.POST)
            if form.is_valid():
                wash_order = form.save(commit=False)
                wash_order.client = client
                
                # Set price based on wash type
                prices = {
                    'basic': 15.00,
                    'premium': 25.00,
                    'deluxe': 35.00
                }
                wash_order.price = prices.get(wash_order.wash_type, 15.00)
                
                # Try to assign an available washer
                from washers.models import Washer
                try:
                    # Debug: Check all washers
                    all_washers = Washer.objects.all()
                    print(f"DEBUG: Total washers in system: {all_washers.count()}")
                    for w in all_washers:
                        print(f"  - {w.full_name}: is_available={w.is_available}, status={w.status}")
                    
                    # Get washers who don't have any active orders
                    washers_with_active_orders = WashOrder.objects.filter(
                        status__in=['assigned', 'in_progress']
                    ).values_list('washer_id', flat=True)
                    print(f"DEBUG: Washers with active orders: {list(washers_with_active_orders)}")
                    
                    available_washers = Washer.objects.filter(
                        is_available=True, 
                        status='active'
                    ).exclude(
                        washer_id__in=washers_with_active_orders
                    )
                    print(f"DEBUG: Available washers found: {available_washers.count()}")
                    
                    available_washer = available_washers.first()
                    
                    if available_washer:
                        wash_order.washer = available_washer
                        wash_order.status = 'assigned'
                        wash_order.assigned_at = timezone.now()
                        
                        print(f"DEBUG: Assigned order to {available_washer.full_name}")
                        messages.success(request, f'Wash order booked successfully! Assigned to {available_washer.full_name}.')
                    else:
                        # No available washers - order will remain pending
                        wash_order.status = 'pending'
                        print(f"DEBUG: No available washers - order set to pending")
                        messages.info(request, 'Wash order booked successfully! All washers are currently busy. We will assign one as soon as possible.')
                except Exception as e:
                    # Log the error for debugging
                    print(f"ERROR assigning washer: {e}")
                    import traceback
                    traceback.print_exc()
                    wash_order.status = 'pending'
                    messages.info(request, 'Wash order booked successfully! We will assign a washer soon.')
                
                wash_order.save()
                return redirect('clients:track_order', order_id=wash_order.order_id)
        else:
            form = WashOrderForm(client=client)
        
        context = {
            'client_name': request.session.get('client_name', 'User'),
            'form': form,
            'title': 'Book a Wash'
        }
        return render(request, 'clients/book_wash.html', context)
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')

def track_order_view(request, order_id):
    """Track a specific wash order"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to access this page.')
        return redirect('clients:login')
    
    client_id = request.session.get('client_id')
    try:
        client = Client.objects.get(client_id=client_id)
        
        # Get the order and make sure it belongs to this client
        try:
            order = WashOrder.objects.get(order_id=order_id, client=client)
            
            # Calculate progress percentage based on status
            progress_map = {
                'pending': 25,
                'assigned': 50,
                'in_progress': 75,
                'completed': 100,
                'cancelled': 0
            }
            
            progress_percentage = progress_map.get(order.status, 25)
            
            # Get status timeline
            timeline = []
            
            # Order placed
            timeline.append({
                'status': 'Order Placed',
                'time': order.created_at,
                'icon': 'fas fa-shopping-cart',
                'completed': True,
                'description': f'Your {order.get_wash_type_display()} wash order has been placed.'
            })
            
            # Assigned to washer
            if order.assigned_at:
                timeline.append({
                    'status': 'Washer Assigned',
                    'time': order.assigned_at,
                    'icon': 'fas fa-user-check',
                    'completed': True,
                    'description': f'Assigned to {order.washer.full_name if order.washer else "a washer"}.'
                })
            else:
                timeline.append({
                    'status': 'Assigning Washer',
                    'time': None,
                    'icon': 'fas fa-user-clock',
                    'completed': False,
                    'description': 'We are finding an available washer for your vehicle.'
                })
            
            # Wash started
            if order.started_at:
                timeline.append({
                    'status': 'Wash Started',
                    'time': order.started_at,
                    'icon': 'fas fa-soap',
                    'completed': True,
                    'description': 'Your vehicle wash is now in progress.'
                })
            elif order.status in ['in_progress', 'completed']:
                timeline.append({
                    'status': 'Wash Started',
                    'time': None,
                    'icon': 'fas fa-soap',
                    'completed': True,
                    'description': 'Your vehicle wash is now in progress.'
                })
            else:
                timeline.append({
                    'status': 'Starting Wash',
                    'time': None,
                    'icon': 'fas fa-soap',
                    'completed': False,
                    'description': 'Wash will begin once washer is ready.'
                })
            
            # Wash completed
            if order.completed_at:
                timeline.append({
                    'status': 'Wash Completed',
                    'time': order.completed_at,
                    'icon': 'fas fa-check-circle',
                    'completed': True,
                    'description': 'Your vehicle is clean and ready for pickup!'
                })
            else:
                timeline.append({
                    'status': 'Completing Wash',
                    'time': None,
                    'icon': 'fas fa-check-circle',
                    'completed': False,
                    'description': 'Final touches and quality check.'
                })
            
            context = {
                'client_name': request.session.get('client_name', 'User'),
                'order': order,
                'progress_percentage': progress_percentage,
                'timeline': timeline,
            }
            return render(request, 'clients/track_order.html', context)
            
        except WashOrder.DoesNotExist:
            messages.error(request, 'Order not found or you do not have permission to view it.')
            return redirect('clients:dashboard')
            
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')

def order_history_view(request):
    """View all client's wash orders"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to access this page.')
        return redirect('clients:login')
    
    client_id = request.session.get('client_id')
    try:
        client = Client.objects.get(client_id=client_id)
        
        # Get all orders for this client
        orders = WashOrder.objects.filter(client=client).order_by('-created_at')
        
        # Calculate statistics
        total_orders = orders.count()
        completed_orders = orders.filter(status='completed').count()
        total_spent = sum(order.price for order in orders)
        
        context = {
            'client_name': request.session.get('client_name', 'User'),
            'orders': orders,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'total_spent': total_spent,
        }
        return render(request, 'clients/order_history.html', context)
        
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')


def schedule_appointment_view(request):
    """Schedule a new appointment with time slot selection"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to schedule an appointment.')
        return redirect('clients:login')
    
    client_id = request.session.get('client_id')
    try:
        client = Client.objects.get(client_id=client_id)
        
        # Check if client has any vehicles
        if not Vehicle.objects.filter(client=client).exists():
            messages.error(request, 'Please add a vehicle first before scheduling.')
            return redirect('clients:add_vehicle')
        
        selected_date = request.GET.get('selected_date') or request.POST.get('date')
        
        if request.method == 'POST':
            print(f"DEBUG: POST data: {request.POST}")
            print(f"DEBUG: Selected date from POST: {selected_date}")
            appointment_form = AppointmentForm(client=client, selected_date=selected_date, data=request.POST)
            
            if appointment_form.is_valid():
                print("DEBUG: Form is valid")
                appointment = appointment_form.save(commit=False)
                appointment.client = client
                appointment.save()
                print(f"DEBUG: Appointment saved: {appointment.id}")
                
                # Create wash order from appointment
                wash_order = appointment.create_wash_order()
                print(f"DEBUG: Wash order created: {wash_order.order_id}")
                
                messages.success(request, f'Appointment scheduled successfully for {appointment.time_slot}!')
                return redirect('clients:track_order', order_id=wash_order.order_id)
            else:
                print(f"DEBUG: Form errors: {appointment_form.errors}")
                messages.error(request, 'Please correct the errors below.')
        else:
            appointment_form = AppointmentForm(client=client, selected_date=selected_date)
        
        # Date selection form
        date_form = TimeSlotSelectionForm(initial={'selected_date': selected_date} if selected_date else None)
        
        # Get available time slots for the selected date
        available_slots = []
        if selected_date:
            from datetime import datetime
            try:
                date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
                # Get all active time slots for the date
                all_slots = TimeSlot.objects.filter(
                    date=date_obj,
                    is_active=True
                )
                
                # Filter out slots that are fully booked
                available_slots = []
                for slot in all_slots:
                    booked_count = slot.appointments.filter(is_cancelled=False).count()
                    if booked_count < slot.max_capacity:
                        available_slots.append(slot)
                print(f"DEBUG: Selected date: {selected_date}")
                print(f"DEBUG: Date object: {date_obj}")
                print(f"DEBUG: Available slots count: {len(available_slots)}")
                for slot in available_slots[:3]:  # Show first 3 slots
                    print(f"DEBUG: Slot: {slot.start_time}-{slot.end_time}, capacity: {slot.max_capacity}")
            except ValueError as e:
                print(f"DEBUG: Date parsing error: {e}")
                pass
        
        context = {
            'client_name': request.session.get('client_name', 'User'),
            'appointment_form': appointment_form,
            'date_form': date_form,
            'selected_date': selected_date,
            'available_slots': available_slots,
            'title': 'Schedule Appointment'
        }
        return render(request, 'clients/schedule_appointment.html', context)
        
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')


def my_appointments_view(request):
    """View client's appointments"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to view appointments.')
        return redirect('clients:login')
    
    client_id = request.session.get('client_id')
    try:
        client = Client.objects.get(client_id=client_id)
        
        # Get upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            client=client,
            is_cancelled=False,
            time_slot__date__gte=timezone.now().date()
        ).select_related('time_slot', 'vehicle', 'wash_order').order_by('time_slot__date', 'time_slot__start_time')
        
        # Get past appointments
        past_appointments = Appointment.objects.filter(
            client=client,
            time_slot__date__lt=timezone.now().date()
        ).select_related('time_slot', 'vehicle', 'wash_order').order_by('-time_slot__date', '-time_slot__start_time')[:10]
        
        context = {
            'client_name': request.session.get('client_name', 'User'),
            'upcoming_appointments': upcoming_appointments,
            'past_appointments': past_appointments,
        }
        return render(request, 'clients/my_appointments.html', context)
        
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')


def cancel_appointment_view(request, appointment_id):
    """Cancel an appointment"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to cancel appointments.')
        return redirect('clients:login')
    
    client_id = request.session.get('client_id')
    try:
        client = Client.objects.get(client_id=client_id)
        appointment = Appointment.objects.get(id=appointment_id, client=client)
        
        if appointment.is_cancelled:
            messages.warning(request, 'This appointment is already cancelled.')
        elif appointment.time_slot.is_past:
            messages.error(request, 'Cannot cancel past appointments.')
        else:
            reason = request.POST.get('reason', 'Cancelled by client')
            appointment.cancel_appointment(reason)
            messages.success(request, f'Appointment for {appointment.time_slot} has been cancelled.')
        
    except (Client.DoesNotExist, Appointment.DoesNotExist):
        messages.error(request, 'Appointment not found.')
    
    return redirect('clients:my_appointments')


def reschedule_appointment_view(request, appointment_id):
    """Reschedule an existing appointment"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to reschedule appointments.')
        return redirect('clients:login')
    
    client_id = request.session.get('client_id')
    try:
        client = Client.objects.get(client_id=client_id)
        appointment = Appointment.objects.get(id=appointment_id, client=client)
        
        if appointment.is_cancelled:
            messages.error(request, 'Cannot reschedule cancelled appointments.')
            return redirect('clients:my_appointments')
        
        if appointment.time_slot.is_past:
            messages.error(request, 'Cannot reschedule past appointments.')
            return redirect('clients:my_appointments')
        
        selected_date = request.GET.get('date')
        
        if request.method == 'POST':
            form = AppointmentForm(client=client, selected_date=selected_date, data=request.POST, instance=appointment)
            
            if form.is_valid():
                form.save()
                messages.success(request, f'Appointment rescheduled to {appointment.time_slot}!')
                return redirect('clients:my_appointments')
        else:
            form = AppointmentForm(client=client, selected_date=selected_date, instance=appointment)
        
        date_form = TimeSlotSelectionForm(initial={'selected_date': selected_date} if selected_date else None)
        
        context = {
            'client_name': request.session.get('client_name', 'User'),
            'form': form,
            'date_form': date_form,
            'appointment': appointment,
            'selected_date': selected_date,
            'title': 'Reschedule Appointment'
        }
        return render(request, 'clients/reschedule_appointment.html', context)
        
    except (Client.DoesNotExist, Appointment.DoesNotExist):
        messages.error(request, 'Appointment not found.')
        return redirect('clients:my_appointments')


def track_order_view(request, order_id):
    """Track a specific order"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to track orders.')
        return redirect('clients:login')
    
    client_id = request.session.get('client_id')
    try:
        client = Client.objects.get(client_id=client_id)
        order = get_object_or_404(WashOrder, order_id=order_id, client=client)
        
        # Get associated appointment if exists
        appointment = None
        try:
            appointment = Appointment.objects.get(wash_order=order)
        except Appointment.DoesNotExist:
            pass
        
        context = {
            'client_name': request.session.get('client_name', 'User'),
            'order': order,
            'appointment': appointment,
            'title': f'Track Order #{order.order_id}'
        }
        return render(request, 'clients/track_order.html', context)
        
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')


def cancel_appointment_view(request, appointment_id):
    """Cancel an appointment"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to cancel appointments.')
        return redirect('clients:login')
    
    client_id = request.session.get('client_id')
    try:
        client = Client.objects.get(client_id=client_id)
        appointment = get_object_or_404(Appointment, id=appointment_id, client=client)
        
        if request.method == 'POST':
            reason = request.POST.get('reason', 'Cancelled by client')
            appointment.cancel_appointment(reason)
            messages.success(request, 'Appointment cancelled successfully.')
            return redirect('clients:my_appointments')
        
        return redirect('clients:my_appointments')
        
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')


def reschedule_appointment_view(request, appointment_id):
    """Reschedule an existing appointment"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to reschedule appointments.')
        return redirect('clients:login')
    
    client_id = request.session.get('client_id')
    try:
        client = Client.objects.get(client_id=client_id)
        appointment = get_object_or_404(Appointment, id=appointment_id, client=client)
        
        if appointment.is_cancelled:
            messages.error(request, 'Cannot reschedule cancelled appointments.')
            return redirect('clients:my_appointments')
        
        if appointment.time_slot.is_past:
            messages.error(request, 'Cannot reschedule past appointments.')
            return redirect('clients:my_appointments')
        
        # For now, redirect to schedule new appointment
        # In a full implementation, you'd create a reschedule form
        messages.info(request, 'Please schedule a new appointment. The old one will be cancelled.')
        return redirect('clients:schedule_appointment')
        
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')


def add_review_view(request, order_id):
    """Add a review for a completed wash order"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to add a review.')
        return redirect('clients:login')
    
    client_id = request.session.get('client_id')
    
    try:
        client = Client.objects.get(client_id=client_id)
        order = WashOrder.objects.get(order_id=order_id, client=client, status='completed')
        
        # Check if review already exists
        if hasattr(order, 'review') and order.review:
            messages.info(request, 'You have already reviewed this order.')
            return redirect('clients:dashboard')
        
        if request.method == 'POST':
            from .models import Review
            
            rating = request.POST.get('rating')
            comment = request.POST.get('comment', '')
            
            if not rating:
                messages.error(request, 'Please select a rating.')
                return render(request, 'clients/add_review.html', {'order': order})
            
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    messages.error(request, 'Rating must be between 1 and 5.')
                    return render(request, 'clients/add_review.html', {'order': order})
                
                # Create review
                review = Review.objects.create(
                    client=client,
                    wash_order=order,
                    washer=order.washer,
                    rating=rating,
                    comment=comment,
                    job_id=order.order_id  # Use order_id as job_id
                )
                
                messages.success(request, 'Thank you for your review!')
                return redirect('clients:dashboard')
                
            except Exception as e:
                messages.error(request, f'Error saving review: {str(e)}')
                return render(request, 'clients/add_review.html', {'order': order})
        
        return render(request, 'clients/add_review.html', {'order': order})
        
    except WashOrder.DoesNotExist:
        messages.error(request, 'Order not found or is not completed.')
        return redirect('clients:dashboard')
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')


def view_reviews_view(request):
    """View all reviews by the client"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to view reviews.')
        return redirect('clients:login')
    
    client_id = request.session.get('client_id')
    client_name = request.session.get('client_name', 'User')
    
    try:
        client = Client.objects.get(client_id=client_id)
        from .models import Review
        
        reviews = Review.objects.filter(client=client).select_related('wash_order', 'washer')
        
        context = {
            'client_name': client_name,
            'reviews': reviews,
        }
        
        return render(request, 'clients/view_reviews.html', context)
        
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')


def client_profile_view(request):
    """View and edit client profile"""
    if 'client_id' not in request.session:
        messages.error(request, 'Please log in to access your profile.')
        return redirect('clients:login')
    
    client_id = request.session.get('client_id')
    client_name = request.session.get('client_name', 'User')
    
    try:
        client = Client.objects.get(client_id=client_id)
        
        # Get stats
        total_orders = 0
        total_cars = 0
        
        try:
            total_orders = WashOrder.objects.filter(client=client).count()
            total_cars = Vehicle.objects.filter(client=client).count()
        except Exception:
            pass
        
        if request.method == 'POST':
            # Update profile
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            
            if not first_name or not last_name:
                messages.error(request, 'First name and last name are required.')
                return render(request, 'clients/profile.html', {
                    'client': client, 
                    'client_name': client_name,
                    'total_orders': total_orders,
                    'total_cars': total_cars,
                })
            
            client.first_name = first_name
            client.last_name = last_name
            client.phone = phone
            client.save()
            
            # Update session
            request.session['client_name'] = f"{first_name} {last_name}"
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('clients:profile')
        
        context = {
            'client': client,
            'client_name': client_name,
            'total_orders': total_orders,
            'total_cars': total_cars,
        }
        
        return render(request, 'clients/profile.html', context)
        
    except Client.DoesNotExist:
        messages.error(request, 'Client account not found.')
        return redirect('clients:login')
