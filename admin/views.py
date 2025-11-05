from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from .forms import AdminLoginForm


def is_admin(user):
    """Check if user is an admin (staff member)"""
    return user.is_authenticated and user.is_staff


def admin_login_view(request):
    """
    Admin login view - no signup option available.
    Only existing admin users can log in.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('carwash_admin:dashboard')
    
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next page or dashboard
            next_page = request.GET.get('next', 'carwash_admin:dashboard')
            return redirect(next_page)
    else:
        form = AdminLoginForm()
    
    return render(request, 'admin/login.html', {'form': form})


def admin_logout_view(request):
    """Admin logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('carwash_admin:login')


@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def admin_dashboard_view(request):
    """Admin dashboard - only accessible to admin users"""
    from .models import SystemStats
    from clients.models import WashOrder
    from washers.models import Washer
    
    # Get dashboard statistics
    stats = SystemStats.get_dashboard_stats()
    print(f"Dashboard stats: {stats}")  # Debug print
    
    # Get pending orders (limit to 6 for dashboard display)
    pending_orders = WashOrder.objects.filter(
        status='pending'
    ).select_related('client', 'vehicle').order_by('-created_at')[:6]
    
    # Get available washers for assignment (those without active orders)
    from django.db.models import Q
    
    # Get washers who don't have any active orders
    washers_with_active_orders = WashOrder.objects.filter(
        status__in=['assigned', 'in_progress']
    ).values_list('washer_id', flat=True)
    
    available_washers = Washer.objects.filter(
        is_available=True
    ).exclude(
        washer_id__in=washers_with_active_orders
    ).order_by('first_name')
    
    context = {
        'user': request.user,
        'title': 'Admin Dashboard',
        'stats': stats,
        'pending_orders': pending_orders,
        'available_washers': available_washers,
    }
    return render(request, 'admin/dashboard.html', context)


def admin_base_view(request):
    """Admin base template view - for testing/development"""
    return render(request, 'admin/base.html', {'title': 'Admin Base Template'})


@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def manage_clients_view(request):
    """View to manage clients - list, view, delete"""
    from clients.models import Client
    
    clients = Client.objects.all().order_by('-date_created')
    
    context = {
        'title': 'Manage Clients',
        'clients': clients,
    }
    return render(request, 'admin/manage_clients.html', context)


@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def delete_client_view(request, client_id):
    """Delete a client"""
    from clients.models import Client
    
    if request.method == 'POST':
        try:
            client = Client.objects.get(client_id=client_id)
            client_name = f"{client.first_name} {client.last_name}"
            client.delete()
            messages.success(request, f'Client {client_name} has been deleted successfully.')
        except Client.DoesNotExist:
            messages.error(request, 'Client not found.')
        except Exception as e:
            messages.error(request, f'Error deleting client: {str(e)}')
    else:
        # Allow GET requests for direct URL access (for testing)
        try:
            client = Client.objects.get(client_id=client_id)
            client_name = f"{client.first_name} {client.last_name}"
            client.delete()
            messages.success(request, f'Client {client_name} has been deleted successfully.')
        except Client.DoesNotExist:
            messages.error(request, 'Client not found.')
        except Exception as e:
            messages.error(request, f'Error deleting client: {str(e)}')
    
    return redirect('carwash_admin:manage_clients')


@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def manage_washers_view(request):
    """View to manage washers - list, view, delete"""
    from washers.models import Washer
    from clients.models import WashOrder
    from django.db.models import Count, Q
    
    washers = Washer.objects.all().order_by('-date_hired')
    
    # Calculate statistics for each washer
    for washer in washers:
        # Get completed orders count
        washer.completed_orders = WashOrder.objects.filter(
            washer=washer, 
            status='completed'
        ).count()
        
        # Get active orders count
        washer.active_orders = WashOrder.objects.filter(
            washer=washer,
            status__in=['assigned', 'in_progress']
        ).count()
        
        # Set a default rating (you can implement a real rating system later)
        washer.rating = 4.8  # Default rating
    
    # Calculate overall statistics
    total_washers = washers.count()
    
    # Get washers with active orders (busy)
    washers_with_active_orders = WashOrder.objects.filter(
        status__in=['assigned', 'in_progress']
    ).values_list('washer_id', flat=True)
    
    busy_washers = len(set(washers_with_active_orders))  # Count unique busy washers
    
    # Available washers are those who are active, available, and don't have active orders
    available_washers = washers.filter(
        is_available=True, 
        status='active'
    ).exclude(
        washer_id__in=washers_with_active_orders
    ).count()
    
    # Offline washers are those who are inactive or on break
    offline_washers = washers.filter(
        Q(is_available=False) | Q(status__in=['inactive', 'on_break'])
    ).count()
    
    context = {
        'title': 'Manage Washers',
        'washers': washers,
        'total_washers': total_washers,
        'available_washers': available_washers,
        'busy_washers': busy_washers,
        'offline_washers': offline_washers,
    }
    return render(request, 'admin/manage_washers.html', context)


@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def delete_washer_view(request, washer_id):
    """Delete a washer"""
    from washers.models import Washer
    
    if request.method == 'POST':
        try:
            washer = Washer.objects.get(washer_id=washer_id)
            washer_name = f"{washer.first_name} {washer.last_name}"
            washer.delete()
            messages.success(request, f'Washer {washer_name} has been deleted successfully.')
        except Washer.DoesNotExist:
            messages.error(request, 'Washer not found.')
        except Exception as e:
            messages.error(request, f'Error deleting washer: {str(e)}')
    else:
        # Allow GET requests for direct URL access (for testing)
        try:
            washer = Washer.objects.get(washer_id=washer_id)
            washer_name = f"{washer.first_name} {washer.last_name}"
            washer.delete()
            messages.success(request, f'Washer {washer_name} has been deleted successfully.')
        except Washer.DoesNotExist:
            messages.error(request, 'Washer not found.')
        except Exception as e:
            messages.error(request, f'Error deleting washer: {str(e)}')
    
    return redirect('carwash_admin:manage_washers')


@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def toggle_washer_status_view(request, washer_id):
    """Toggle washer availability status"""
    from washers.models import Washer
    
    try:
        washer = Washer.objects.get(washer_id=washer_id)
        washer.is_available = not washer.is_available
        washer.save()
        
        status = "available" if washer.is_available else "unavailable"
        messages.success(request, f'Washer {washer.first_name} {washer.last_name} is now {status}.')
    except Washer.DoesNotExist:
        messages.error(request, 'Washer not found.')
    
    return redirect('carwash_admin:manage_washers')


@csrf_protect
@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def add_washer_view(request):
    """Add a new washer/staff member"""
    from washers.forms import AdminAddWasherForm
    from washers.models import Washer
    from django.contrib.auth.hashers import make_password
    
    if request.method == 'POST':
        form = AdminAddWasherForm(request.POST)
        if form.is_valid():
            try:
                # Create washer instance but don't save yet
                washer = form.save(commit=False)
                # Hash the password
                washer.password_hash = make_password(form.cleaned_data['password'])
                washer.save()
                
                messages.success(
                    request, 
                    f'Staff member {washer.first_name} {washer.last_name} has been added successfully!'
                )
                return redirect('carwash_admin:manage_washers')
            except Exception as e:
                messages.error(request, f'Error adding staff member: {str(e)}')
        else:
            # Form has validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.title()}: {error}')
    else:
        form = AdminAddWasherForm()
    
    context = {
        'title': 'Add New Staff Member',
        'form': form,
    }
    return render(request, 'admin/add_washer.html', context)

@csrf_protect
@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def edit_washer_view(request, washer_id):
    """Edit an existing washer/staff member"""
    from washers.forms import AdminEditWasherForm
    from washers.models import Washer
    from django.shortcuts import get_object_or_404
    from django.contrib.auth.hashers import make_password
    
    washer = get_object_or_404(Washer, washer_id=washer_id)
    
    if request.method == 'POST':
        form = AdminEditWasherForm(request.POST, instance=washer)
        if form.is_valid():
            try:
                # Save the form but don't commit yet if password is being changed
                updated_washer = form.save(commit=False)
                
                # Check if password is being changed
                new_password = form.cleaned_data.get('new_password')
                if new_password:
                    updated_washer.password_hash = make_password(new_password)
                
                updated_washer.save()
                
                messages.success(
                    request, 
                    f'Staff member {updated_washer.first_name} {updated_washer.last_name} has been updated successfully!'
                )
                return redirect('carwash_admin:manage_washers')
            except Exception as e:
                messages.error(request, f'Error updating staff member: {str(e)}')
        else:
            # Form has validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.title()}: {error}')
    else:
        form = AdminEditWasherForm(instance=washer)
    
    context = {
        'title': f'Edit Staff Member - {washer.first_name} {washer.last_name}',
        'form': form,
        'washer': washer,
    }
    return render(request, 'admin/edit_washer.html', context)

@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def manage_orders_view(request):
    """View to manage wash orders"""
    from clients.models import WashOrder
    from django.utils import timezone
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    date_filter = request.GET.get('date', 'all')
    
    # Base queryset
    orders = WashOrder.objects.all().select_related('client', 'vehicle', 'washer')
    
    # Apply status filter
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    # Apply date filter
    if date_filter == 'today':
        orders = orders.filter(created_at__date=timezone.now().date())
    elif date_filter == 'week':
        week_ago = timezone.now() - timezone.timedelta(days=7)
        orders = orders.filter(created_at__gte=week_ago)
    elif date_filter == 'month':
        month_ago = timezone.now() - timezone.timedelta(days=30)
        orders = orders.filter(created_at__gte=month_ago)
    
    orders = orders.order_by('-created_at')
    
    # Get statistics for the filtered orders
    total_orders = orders.count()
    total_revenue = sum(order.price for order in orders)
    
    context = {
        'title': 'Manage Orders',
        'orders': orders,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'status_choices': WashOrder.STATUS_CHOICES,
    }
    return render(request, 'admin/manage_orders.html', context)


@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def assign_washer_view(request, order_id):
    """Assign a washer to an order"""
    from clients.models import WashOrder
    from washers.models import Washer
    from django.utils import timezone
    
    try:
        order = WashOrder.objects.get(order_id=order_id)
        
        if request.method == 'POST':
            washer_id = request.POST.get('washer_id')
            if washer_id:
                try:
                    washer = Washer.objects.get(washer_id=washer_id)
                    
                    # Check if washer already has an active order
                    active_orders = WashOrder.objects.filter(
                        washer=washer,
                        status__in=['assigned', 'in_progress']
                    ).count()
                    
                    if active_orders > 0:
                        messages.error(request, 
                            f'Cannot assign order to {washer.full_name}. '
                            f'This washer already has {active_orders} active order(s). '
                            f'Please wait for current orders to be completed.'
                        )
                    else:
                        # Assign washer to order
                        order.washer = washer
                        order.status = 'assigned'
                        order.assigned_at = timezone.now()
                        order.save()
                        
                        # Don't mark washer as unavailable - they can get new orders after completing current one
                        
                        messages.success(request, f'Order #{order.order_id} assigned to {washer.full_name}.')
                        
                except Washer.DoesNotExist:
                    messages.error(request, 'Washer not found.')
            else:
                messages.error(request, 'Please select a washer.')
        
    except WashOrder.DoesNotExist:
        messages.error(request, 'Order not found.')
    
    return redirect('carwash_admin:manage_orders')


@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def cancel_order_view(request, order_id):
    """Cancel an order"""
    from clients.models import WashOrder
    
    try:
        order = WashOrder.objects.get(order_id=order_id)
        
        # Check if order can be cancelled
        if order.status == 'cancelled':
            messages.warning(request, f'Order #{order.order_id} is already cancelled.')
        elif order.status == 'completed':
            messages.error(request, f'Cannot cancel completed order #{order.order_id}.')
        else:
            # If order was assigned, make washer available again
            if order.washer and order.status in ['assigned', 'in_progress']:
                order.washer.is_available = True
                order.washer.save()
            
            # Get cancellation reason if provided
            cancellation_reason = request.POST.get('cancellation_reason', '')
            
            order.status = 'cancelled'
            # You could add a cancellation_reason field to the model if needed
            # order.cancellation_reason = cancellation_reason
            order.save()
            
            if cancellation_reason:
                messages.success(request, f'Order #{order.order_id} has been cancelled. Reason: {cancellation_reason}')
            else:
                messages.success(request, f'Order #{order.order_id} has been cancelled.')
        
    except WashOrder.DoesNotExist:
        messages.error(request, 'Order not found.')
    except Exception as e:
        messages.error(request, f'Error cancelling order: {str(e)}')
    
    # Check where the request came from and redirect appropriately
    referer = request.META.get('HTTP_REFERER', '')
    if 'dashboard' in referer:
        return redirect('carwash_admin:dashboard')
    else:
        return redirect('carwash_admin:manage_orders')


@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def analytics_view(request):
    """Analytics and reporting view"""
    from clients.models import WashOrder, Client, Vehicle
    from washers.models import Washer
    from django.utils import timezone
    from django.db.models import Count, Sum, Avg
    from decimal import Decimal
    
    # Date ranges
    today = timezone.now().date()
    week_ago = today - timezone.timedelta(days=7)
    month_ago = today - timezone.timedelta(days=30)
    year_ago = today - timezone.timedelta(days=365)
    
    # Revenue analytics
    revenue_today = WashOrder.objects.filter(
        created_at__date=today, status='completed'
    ).aggregate(total=Sum('price'))['total'] or 0
    
    revenue_week = WashOrder.objects.filter(
        created_at__date__gte=week_ago, status='completed'
    ).aggregate(total=Sum('price'))['total'] or 0
    
    revenue_month = WashOrder.objects.filter(
        created_at__date__gte=month_ago, status='completed'
    ).aggregate(total=Sum('price'))['total'] or 0
    
    # Total orders and customers
    total_orders = WashOrder.objects.filter(created_at__date__gte=month_ago).count()
    completed_orders = WashOrder.objects.filter(
        created_at__date__gte=month_ago, status='completed'
    ).count()
    
    # New customers this month
    new_customers = Client.objects.filter(
        date_created__date__gte=month_ago
    ).count()
    
    # Average order value
    avg_order_value = WashOrder.objects.filter(
        created_at__date__gte=month_ago, status='completed'
    ).aggregate(avg=Avg('price'))['avg'] or 0
    
    # Completion rate
    completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
    
    # Average rating (placeholder - you can implement actual ratings later)
    avg_rating = 4.8
    
    # Peak day analysis
    from django.db.models import Q
    import calendar
    
    # Get orders by day of week for the past month
    orders_by_weekday = {}
    for i in range(7):  # 0=Monday, 6=Sunday
        day_orders = WashOrder.objects.filter(
            created_at__date__gte=month_ago,
            created_at__week_day=i+2  # Django uses 1=Sunday, 2=Monday
        ).count()
        orders_by_weekday[calendar.day_name[i]] = day_orders
    
    peak_day = max(orders_by_weekday, key=orders_by_weekday.get) if orders_by_weekday else "Saturday"
    peak_day_orders = orders_by_weekday.get(peak_day, 25)
    
    # Repeat customers analysis
    repeat_customers_count = Client.objects.annotate(
        order_count=Count('washorder')
    ).filter(order_count__gt=1).count()
    
    total_customers = Client.objects.count()
    repeat_customers_percentage = (repeat_customers_count / total_customers * 100) if total_customers > 0 else 0
    
    # Service efficiency
    avg_service_time = 45  # Placeholder - you can calculate actual service time
    
    # Cancellation rate
    cancelled_orders = WashOrder.objects.filter(
        created_at__date__gte=month_ago, status='cancelled'
    ).count()
    cancellation_rate = (cancelled_orders / total_orders * 100) if total_orders > 0 else 0
    
    # Revenue growth (compare with previous month)
    prev_month_start = month_ago - timezone.timedelta(days=30)
    prev_month_revenue = WashOrder.objects.filter(
        created_at__date__gte=prev_month_start,
        created_at__date__lt=month_ago,
        status='completed'
    ).aggregate(total=Sum('price'))['total'] or 1
    
    revenue_growth = ((revenue_month - prev_month_revenue) / prev_month_revenue * 100) if prev_month_revenue > 0 else 0
    
    # Order analytics
    orders_by_status = WashOrder.objects.values('status').annotate(count=Count('status'))
    orders_by_type = WashOrder.objects.values('wash_type').annotate(count=Count('wash_type'))
    
    # Top performing washers
    top_washers = WashOrder.objects.filter(
        status='completed',
        created_at__date__gte=month_ago
    ).values(
        'washer__first_name', 'washer__last_name'
    ).annotate(
        completed_orders=Count('order_id'),
        total_revenue=Sum('price')
    ).order_by('-completed_orders')[:5]
    
    # Recent activity
    recent_orders = WashOrder.objects.select_related(
        'client', 'vehicle', 'washer'
    ).order_by('-created_at')[:10]
    
    # Revenue trend data for the past 30 days
    revenue_trend_data = []
    revenue_trend_labels = []
    
    for i in range(29, -1, -1):  # Last 30 days
        date = today - timezone.timedelta(days=i)
        daily_revenue = WashOrder.objects.filter(
            created_at__date=date,
            status='completed'
        ).aggregate(total=Sum('price'))['total'] or 0
        
        revenue_trend_data.append(float(daily_revenue))
        revenue_trend_labels.append(date.strftime('%m/%d'))
    
    # Service distribution data for pie chart
    service_distribution = WashOrder.objects.filter(
        created_at__date__gte=month_ago
    ).values('wash_type').annotate(
        count=Count('wash_type'),
        revenue=Sum('price')
    ).order_by('-count')
    
    # Prepare data for pie chart
    service_labels = []
    service_counts = []
    service_colors = [
        '#023859',  # Primary blue
        '#a7ebf2',  # Secondary blue
        '#28a745',  # Success green
        '#ffc107',  # Warning yellow
        '#dc3545',  # Danger red
        '#17a2b8',  # Info cyan
        '#6f42c1',  # Purple
        '#fd7e14',  # Orange
    ]
    
    for i, service in enumerate(service_distribution):
        service_labels.append(service['wash_type'].replace('_', ' ').title())
        service_counts.append(service['count'])
    
    # If no services, add placeholder data
    if not service_labels:
        service_labels = ['Basic Wash', 'Premium Wash', 'Deluxe Wash']
        service_counts = [5, 3, 2]
    
    # Daily orders overview - orders by day of the week
    import calendar
    daily_orders_data = []
    daily_orders_labels = []
    
    # Get orders for each day of the week (last 30 days)
    for day_num in range(7):  # 0=Monday, 6=Sunday
        day_name = calendar.day_name[day_num]
        # Django week_day: 1=Sunday, 2=Monday, ..., 7=Saturday
        django_day_num = (day_num + 2) % 7
        if django_day_num == 0:
            django_day_num = 7
            
        day_orders = WashOrder.objects.filter(
            created_at__date__gte=month_ago,
            created_at__week_day=django_day_num
        ).count()
        
        daily_orders_data.append(day_orders)
        daily_orders_labels.append(day_name)
    
    # Order status distribution for additional insights
    status_distribution = []
    status_labels = []
    status_colors = ['#28a745', '#ffc107', '#dc3545', '#17a2b8', '#6f42c1']
    
    for status_choice in WashOrder.STATUS_CHOICES:
        status_code = status_choice[0]
        status_name = status_choice[1]
        count = WashOrder.objects.filter(
            created_at__date__gte=month_ago,
            status=status_code
        ).count()
        
        if count > 0:  # Only include statuses that have orders
            status_distribution.append(count)
            status_labels.append(status_name)
    
    # Create analytics object for template
    analytics = {
        'total_revenue': float(revenue_month),
        'total_orders': total_orders,
        'new_customers': new_customers,
        'avg_order_value': float(avg_order_value) if avg_order_value else 0,
        'completion_rate': round(completion_rate, 1),
        'avg_rating': avg_rating,
        'peak_day_orders': peak_day_orders,
        'repeat_customers': round(repeat_customers_percentage, 1),
        'avg_service_time': avg_service_time,
        'cancellation_rate': round(cancellation_rate, 1),
        'revenue_growth': round(revenue_growth, 1),
    }
    
    context = {
        'title': 'Analytics & Reports',
        'analytics': analytics,
        'revenue_today': revenue_today,
        'revenue_week': revenue_week,
        'revenue_month': revenue_month,
        'orders_by_status': orders_by_status,
        'orders_by_type': orders_by_type,
        'top_washers': top_washers,
        'recent_orders': recent_orders,
        'revenue_trend_data': revenue_trend_data,
        'revenue_trend_labels': revenue_trend_labels,
        'service_labels': service_labels,
        'service_counts': service_counts,
        'service_colors': service_colors[:len(service_labels)],
        'daily_orders_data': daily_orders_data,
        'daily_orders_labels': daily_orders_labels,
        'status_distribution': status_distribution,
        'status_labels': status_labels,
        'status_colors': status_colors[:len(status_labels)],
    }
    return render(request, 'admin/analytics.html', context)


@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def manage_appointments_view(request):
    """View to manage appointments - list, view, cancel"""
    from clients.models import Appointment
    from django.utils import timezone
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        is_cancelled=False,
        time_slot__date__gte=timezone.now().date()
    ).select_related('client', 'vehicle', 'time_slot', 'wash_order').order_by('time_slot__date', 'time_slot__start_time')
    
    # Get past appointments (last 30 days)
    past_appointments = Appointment.objects.filter(
        time_slot__date__lt=timezone.now().date(),
        time_slot__date__gte=timezone.now().date() - timezone.timedelta(days=30)
    ).select_related('client', 'vehicle', 'time_slot', 'wash_order').order_by('-time_slot__date', '-time_slot__start_time')[:20]
    
    context = {
        'user': request.user,
        'title': 'Manage Appointments',
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
    }
    return render(request, 'admin/manage_appointments.html', context)


@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def cancel_appointment_admin_view(request, appointment_id):
    """Cancel an appointment from admin panel"""
    from clients.models import Appointment
    from django.shortcuts import get_object_or_404
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Cancelled by admin')
        
        try:
            # Cancel the appointment
            appointment.cancel_appointment(reason)
            
            messages.success(request, f'Appointment for {appointment.client.first_name} {appointment.client.last_name} on {appointment.time_slot.date} has been cancelled.')
        except Exception as e:
            messages.error(request, f'Error cancelling appointment: {str(e)}')
    
    return redirect('carwash_admin:manage_appointments')