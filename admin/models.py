from django.db import models
from clients.models import Client
from washers.models import Washer
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

# Admin-specific models for managing the car wash system
class SystemStats:
    """Helper class for system statistics"""
    
    @staticmethod
    def get_dashboard_stats():
        """Get statistics for admin dashboard"""
        stats = {
            'total_orders': 0,
            'pending_orders': 0,
            'in_progress_orders': 0,
            'completed_today': 0,
            'total_clients': 0,
            'total_washers': 0,
            'available_washers': 0,
            'total_cars': 0,
            'total_revenue': 0,
        }
        
        try:
            stats['total_clients'] = Client.objects.count()
        except Exception as e:
            print(f"Error getting clients count: {e}")
            
        try:
            stats['total_washers'] = Washer.objects.count()
            
            # Get truly available washers (those without active orders)
            from clients.models import WashOrder
            washers_with_active_orders = WashOrder.objects.filter(
                status__in=['assigned', 'in_progress']
            ).values_list('washer_id', flat=True)
            
            stats['available_washers'] = Washer.objects.filter(
                is_available=True
            ).exclude(
                washer_id__in=washers_with_active_orders
            ).count()
            
        except Exception as e:
            print(f"Error getting washers count: {e}")
            
        try:
            from clients.models import Vehicle
            stats['total_cars'] = Vehicle.objects.count()
        except Exception as e:
            print(f"Error getting vehicles count: {e}")
            
        try:
            from clients.models import WashOrder, Appointment
            
            # Count all orders
            stats['total_orders'] = WashOrder.objects.count()
            stats['pending_orders'] = WashOrder.objects.filter(status='pending').count()
            stats['in_progress_orders'] = WashOrder.objects.filter(status='in_progress').count()
            stats['completed_today'] = WashOrder.objects.filter(
                status='completed',
                completed_at__date=timezone.now().date()
            ).count()
            
            # Also count scheduled appointments (those without wash orders yet or with pending orders)
            scheduled_appointments = Appointment.objects.filter(
                is_cancelled=False,
                time_slot__date__gte=timezone.now().date()
            ).count()
            
            # Add scheduled appointments to pending orders count
            stats['scheduled_appointments'] = scheduled_appointments
            
            # Calculate total revenue from completed orders
            completed_orders = WashOrder.objects.filter(status='completed')
            stats['total_revenue'] = sum(order.price for order in completed_orders if order.price)
            
            print(f"DEBUG: Orders stats - Total: {stats['total_orders']}, Pending: {stats['pending_orders']}, Scheduled: {scheduled_appointments}")
            
        except Exception as e:
            print(f"Error getting orders data: {e}")
            
        return stats
