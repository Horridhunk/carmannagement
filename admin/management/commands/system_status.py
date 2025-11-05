from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clients.models import Client, Vehicle, WashOrder
from washers.models import Washer
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Display system status and statistics'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Car Wash Management System Status ===')
        )

        # User statistics
        total_users = User.objects.count()
        admin_users = User.objects.filter(is_staff=True).count()
        regular_users = total_users - admin_users

        self.stdout.write('\n📊 User Statistics:')
        self.stdout.write(f'  Total Users: {total_users}')
        self.stdout.write(f'  Admin Users: {admin_users}')
        self.stdout.write(f'  Regular Users: {regular_users}')

        # Client statistics
        total_clients = Client.objects.count()
        active_clients = Client.objects.filter(user__is_active=True).count()

        self.stdout.write('\n👥 Client Statistics:')
        self.stdout.write(f'  Total Clients: {total_clients}')
        self.stdout.write(f'  Active Clients: {active_clients}')

        # Vehicle statistics
        total_vehicles = Vehicle.objects.count()
        
        self.stdout.write('\n🚗 Vehicle Statistics:')
        self.stdout.write(f'  Total Vehicles: {total_vehicles}')
        
        if total_vehicles > 0:
            # Most common makes
            from django.db.models import Count
            popular_makes = Vehicle.objects.values('make').annotate(
                count=Count('make')
            ).order_by('-count')[:3]
            
            self.stdout.write('  Popular Makes:')
            for make in popular_makes:
                self.stdout.write(f'    - {make["make"]}: {make["count"]} vehicles')

        # Washer statistics
        total_washers = Washer.objects.count()
        available_washers = Washer.objects.filter(is_available=True).count()
        busy_washers = total_washers - available_washers

        self.stdout.write('\n👨‍💼 Staff Statistics:')
        self.stdout.write(f'  Total Washers: {total_washers}')
        self.stdout.write(f'  Available: {available_washers}')
        self.stdout.write(f'  Busy: {busy_washers}')

        # Order statistics
        total_orders = WashOrder.objects.count()
        
        # Orders by status
        pending_orders = WashOrder.objects.filter(status='pending').count()
        in_progress_orders = WashOrder.objects.filter(status='in_progress').count()
        completed_orders = WashOrder.objects.filter(status='completed').count()
        cancelled_orders = WashOrder.objects.filter(status='cancelled').count()

        self.stdout.write('\n📦 Order Statistics:')
        self.stdout.write(f'  Total Orders: {total_orders}')
        self.stdout.write(f'  Pending: {pending_orders}')
        self.stdout.write(f'  In Progress: {in_progress_orders}')
        self.stdout.write(f'  Completed: {completed_orders}')
        self.stdout.write(f'  Cancelled: {cancelled_orders}')

        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_orders = WashOrder.objects.filter(created_at__gte=week_ago).count()
        recent_clients = Client.objects.filter(date_created__gte=week_ago).count()

        self.stdout.write('\n📈 Recent Activity (Last 7 Days):')
        self.stdout.write(f'  New Orders: {recent_orders}')
        self.stdout.write(f'  New Clients: {recent_clients}')

        # Revenue statistics
        if total_orders > 0:
            from django.db.models import Sum, Avg
            total_revenue = WashOrder.objects.filter(
                status='completed'
            ).aggregate(total=Sum('price'))['total'] or 0
            
            avg_order_value = WashOrder.objects.filter(
                status='completed'
            ).aggregate(avg=Avg('price'))['avg'] or 0

            self.stdout.write('\n💰 Revenue Statistics:')
            self.stdout.write(f'  Total Revenue: ${total_revenue:.2f}')
            self.stdout.write(f'  Average Order Value: ${avg_order_value:.2f}')

        # System health
        self.stdout.write('\n🏥 System Health:')
        
        # Check for potential issues
        issues = []
        
        if admin_users == 0:
            issues.append('No admin users found!')
        
        if total_washers == 0:
            issues.append('No washers registered!')
        
        if available_washers == 0 and total_washers > 0:
            issues.append('No washers available!')
        
        if pending_orders > 0 and available_washers == 0:
            issues.append(f'{pending_orders} pending orders but no available washers!')

        if issues:
            self.stdout.write('  ⚠️  Issues Found:')
            for issue in issues:
                self.stdout.write(f'    - {issue}')
        else:
            self.stdout.write('  ✅ No issues detected')

        self.stdout.write(
            self.style.SUCCESS('\n=== End of System Status ===')
        )