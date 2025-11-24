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
    """Toggle washer availability status and auto-assign pending orders"""
    from washers.models import Washer
    from clients.utils import auto_assign_pending_orders
    
    try:
        washer = Washer.objects.get(washer_id=washer_id)
        washer.is_available = not washer.is_available
        washer.save()
        
        status = "available" if washer.is_available else "unavailable"
        messages.success(request, f'Washer {washer.first_name} {washer.last_name} is now {status}.')
        
        # If washer is now available, try to auto-assign pending orders
        if washer.is_available:
            assigned_count = auto_assign_pending_orders()
            if assigned_count > 0:
                messages.success(request, f'Automatically assigned {assigned_count} pending order(s) to available washers.')
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
    """Cancel an order and auto-assign pending orders"""
    from clients.models import WashOrder
    from clients.utils import auto_assign_pending_orders
    
    try:
        order = WashOrder.objects.get(order_id=order_id)
        
        # Check if order can be cancelled
        if order.status == 'cancelled':
            messages.warning(request, f'Order #{order.order_id} is already cancelled.')
        elif order.status == 'completed':
            messages.error(request, f'Cannot cancel completed order #{order.order_id}.')
        else:
            # Track if washer was freed up
            washer_freed = False
            
            # If order was assigned, make washer available again
            if order.washer and order.status in ['assigned', 'in_progress']:
                order.washer.is_available = True
                order.washer.save()
                washer_freed = True
            
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
            
            # If a washer was freed up, try to auto-assign pending orders
            if washer_freed:
                assigned_count = auto_assign_pending_orders()
                if assigned_count > 0:
                    messages.success(request, f'Automatically assigned {assigned_count} pending order(s) to available washers.')
        
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
    """Analytics and reporting view with robust error handling"""
    from clients.models import WashOrder, Client, Vehicle
    from washers.models import Washer
    from django.utils import timezone
    from django.db.models import Count, Sum, Avg, Q
    from decimal import Decimal
    import calendar
    
    # Get date range from request parameters or use defaults
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Default date ranges
    today = timezone.now().date()
    week_ago = today - timezone.timedelta(days=7)
    month_ago = today - timezone.timedelta(days=30)
    
    # Parse custom date range if provided
    try:
        if start_date_str and end_date_str:
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            start_date = month_ago
            end_date = today
    except ValueError:
        # Fallback to default if date parsing fails
        start_date = month_ago
        end_date = today
    
    # Ensure start_date is not after end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    # Revenue analytics with safe defaults
    try:
        revenue_today = WashOrder.objects.filter(
            created_at__date=today, status='completed'
        ).aggregate(total=Sum('price'))['total'] or Decimal('0.00')
        
        revenue_week = WashOrder.objects.filter(
            created_at__date__gte=week_ago, status='completed'
        ).aggregate(total=Sum('price'))['total'] or Decimal('0.00')
        
        revenue_period = WashOrder.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='completed'
        ).aggregate(total=Sum('price'))['total'] or Decimal('0.00')
    except Exception as e:
        print(f"Revenue calculation error: {e}")
        revenue_today = revenue_week = revenue_period = Decimal('0.00')
    
    # Order analytics with safe defaults
    try:
        total_orders = WashOrder.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).count()
        
        completed_orders = WashOrder.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='completed'
        ).count()
        
        cancelled_orders = WashOrder.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='cancelled'
        ).count()
    except Exception as e:
        print(f"Order count error: {e}")
        total_orders = completed_orders = cancelled_orders = 0
    
    # Customer analytics with safe defaults
    try:
        new_customers = Client.objects.filter(
            date_created__date__gte=start_date,
            date_created__date__lte=end_date
        ).count()
        
        total_customers = Client.objects.count()
        
        # Repeat customers analysis
        repeat_customers_count = Client.objects.annotate(
            order_count=Count('washorder')
        ).filter(order_count__gt=1).count()
        
        repeat_customers_percentage = (
            (repeat_customers_count / total_customers * 100) 
            if total_customers > 0 else 0
        )
    except Exception as e:
        print(f"Customer analytics error: {e}")
        new_customers = total_customers = repeat_customers_count = 0
        repeat_customers_percentage = 0
    
    # Calculate rates with safe division
    try:
        avg_order_value = WashOrder.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='completed'
        ).aggregate(avg=Avg('price'))['avg'] or Decimal('0.00')
        
        completion_rate = (
            (completed_orders / total_orders * 100) 
            if total_orders > 0 else 100.0
        )
        
        cancellation_rate = (
            (cancelled_orders / total_orders * 100) 
            if total_orders > 0 else 0.0
        )
    except Exception as e:
        print(f"Rate calculation error: {e}")
        avg_order_value = Decimal('0.00')
        completion_rate = cancellation_rate = 0.0
    
    # Peak day analysis with fallbacks
    try:
        orders_by_weekday = {}
        for i in range(7):  # 0=Monday, 6=Sunday
            # Django week_day: 1=Sunday, 2=Monday, ..., 7=Saturday
            django_day_num = (i + 2) % 7
            if django_day_num == 0:
                django_day_num = 7
                
            day_orders = WashOrder.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date,
                created_at__week_day=django_day_num
            ).count()
            orders_by_weekday[calendar.day_name[i]] = day_orders
        
        if any(orders_by_weekday.values()):
            peak_day = max(orders_by_weekday, key=orders_by_weekday.get)
            peak_day_orders = orders_by_weekday[peak_day]
        else:
            peak_day = "No data"
            peak_day_orders = 0
    except Exception as e:
        print(f"Peak day analysis error: {e}")
        peak_day = "Saturday"
        peak_day_orders = 0
        orders_by_weekday = {day: 0 for day in calendar.day_name}
    
    # Revenue growth calculation with safe division
    try:
        # Calculate previous period for comparison
        period_length = (end_date - start_date).days
        prev_start = start_date - timezone.timedelta(days=period_length)
        prev_end = start_date - timezone.timedelta(days=1)
        
        prev_period_revenue = WashOrder.objects.filter(
            created_at__date__gte=prev_start,
            created_at__date__lte=prev_end,
            status='completed'
        ).aggregate(total=Sum('price'))['total'] or Decimal('0.00')
        
        if prev_period_revenue > 0:
            revenue_growth = float((revenue_period - prev_period_revenue) / prev_period_revenue * 100)
        else:
            revenue_growth = 100.0 if revenue_period > 0 else 0.0
    except Exception as e:
        print(f"Revenue growth calculation error: {e}")
        revenue_growth = 0.0
    
    # Chart data preparation with fallbacks
    try:
        # Revenue trend data
        revenue_trend_data = []
        revenue_trend_labels = []
        
        current_date = start_date
        while current_date <= end_date:
            daily_revenue = WashOrder.objects.filter(
                created_at__date=current_date,
                status='completed'
            ).aggregate(total=Sum('price'))['total'] or Decimal('0.00')
            
            revenue_trend_data.append(float(daily_revenue))
            revenue_trend_labels.append(current_date.strftime('%m/%d'))
            current_date += timezone.timedelta(days=1)
        
        # Limit to last 30 days for readability
        if len(revenue_trend_data) > 30:
            revenue_trend_data = revenue_trend_data[-30:]
            revenue_trend_labels = revenue_trend_labels[-30:]
    except Exception as e:
        print(f"Revenue trend data error: {e}")
        revenue_trend_data = [0] * 30
        revenue_trend_labels = [(today - timezone.timedelta(days=i)).strftime('%m/%d') for i in range(29, -1, -1)]
    
    # Service distribution with fallbacks
    try:
        service_distribution = WashOrder.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).values('wash_type').annotate(
            count=Count('wash_type')
        ).order_by('-count')
        
        service_labels = []
        service_counts = []
        
        for service in service_distribution:
            service_labels.append(service['wash_type'].replace('_', ' ').title())
            service_counts.append(service['count'])
        
        # Fallback data if no services
        if not service_labels:
            service_labels = ['No Data Available']
            service_counts = [1]
    except Exception as e:
        print(f"Service distribution error: {e}")
        service_labels = ['Basic Wash']
        service_counts = [1]
    
    # Daily orders data with safe handling
    try:
        daily_orders_data = []
        daily_orders_labels = []
        
        for day_num in range(7):  # 0=Monday, 6=Sunday
            day_name = calendar.day_name[day_num]
            day_orders = orders_by_weekday.get(day_name, 0)
            
            daily_orders_data.append(day_orders)
            daily_orders_labels.append(day_name)
    except Exception as e:
        print(f"Daily orders data error: {e}")
        daily_orders_data = [0] * 7
        daily_orders_labels = list(calendar.day_name)
    
    # Top washers with safe handling
    try:
        top_washers = WashOrder.objects.filter(
            status='completed',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            washer__isnull=False
        ).values(
            'washer__first_name', 'washer__last_name'
        ).annotate(
            completed_orders=Count('order_id'),
            total_revenue=Sum('price')
        ).order_by('-completed_orders')[:5]
    except Exception as e:
        print(f"Top washers error: {e}")
        top_washers = []
    
    # Create analytics object with safe values
    analytics = {
        'total_revenue': float(revenue_period),
        'total_orders': total_orders,
        'new_customers': new_customers,
        'avg_order_value': float(avg_order_value),
        'completion_rate': round(completion_rate, 1),
        'avg_rating': 4.8,  # Placeholder until rating system is implemented
        'peak_day_orders': peak_day_orders,
        'peak_day': peak_day,
        'repeat_customers': round(repeat_customers_percentage, 1),
        'avg_service_time': 45,  # Placeholder
        'cancellation_rate': round(cancellation_rate, 1),
        'revenue_growth': round(revenue_growth, 1),
    }
    
    # Color schemes
    service_colors = [
        '#023859', '#a7ebf2', '#28a745', '#ffc107', '#dc3545', 
        '#17a2b8', '#6f42c1', '#fd7e14'
    ]
    
    context = {
        'title': 'Analytics & Reports',
        'analytics': analytics,
        'revenue_today': float(revenue_today),
        'revenue_week': float(revenue_week),
        'revenue_period': float(revenue_period),
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'top_washers': top_washers,
        'revenue_trend_data': revenue_trend_data,
        'revenue_trend_labels': revenue_trend_labels,
        'service_labels': service_labels,
        'service_counts': service_counts,
        'service_colors': service_colors[:len(service_labels)],
        'daily_orders_data': daily_orders_data,
        'daily_orders_labels': daily_orders_labels,
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


@login_required(login_url='/carwash-admin/login/')
@user_passes_test(is_admin, login_url='/carwash-admin/login/')
def auto_assign_orders_view(request):
    """Manually trigger auto-assignment of pending orders"""
    from clients.utils import auto_assign_pending_orders
    
    try:
        assigned_count = auto_assign_pending_orders()
        
        if assigned_count > 0:
            messages.success(request, f'Successfully assigned {assigned_count} pending order(s) to available washers.')
        else:
            messages.info(request, 'No pending orders to assign or no available washers.')
    except Exception as e:
        messages.error(request, f'Error auto-assigning orders: {str(e)}')
    
    # Redirect back to the referring page or dashboard
    referer = request.META.get('HTTP_REFERER', '')
    if 'orders' in referer:
        return redirect('carwash_admin:manage_orders')
    else:
        return redirect('carwash_admin:dashboard')
