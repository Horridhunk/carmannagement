# clients/utils.py
"""
Utility functions for client operations
"""
from django.utils import timezone
from .models import WashOrder
from washers.models import Washer


def auto_assign_pending_orders():
    """
    Automatically assign pending orders to available washers.
    Returns the number of orders assigned.
    """
    assigned_count = 0
    
    # Get all pending orders ordered by creation time (FIFO)
    pending_orders = WashOrder.objects.filter(
        status='pending'
    ).order_by('created_at')
    
    if not pending_orders.exists():
        return 0
    
    # Get washers who don't have any active orders
    washers_with_active_orders = WashOrder.objects.filter(
        status__in=['assigned', 'in_progress']
    ).values_list('washer_id', flat=True)
    
    available_washers = Washer.objects.filter(
        is_available=True,
        status='active'
    ).exclude(
        washer_id__in=washers_with_active_orders
    ).order_by('date_hired')  # Prioritize by seniority or any other criteria
    
    # Assign orders to available washers
    for order in pending_orders:
        # Check if there are still available washers
        # Re-query to get fresh list since we're assigning in a loop
        washers_with_active_orders = WashOrder.objects.filter(
            status__in=['assigned', 'in_progress']
        ).values_list('washer_id', flat=True)
        
        available_washer = Washer.objects.filter(
            is_available=True,
            status='active'
        ).exclude(
            washer_id__in=washers_with_active_orders
        ).first()
        
        if available_washer:
            order.washer = available_washer
            order.status = 'assigned'
            order.assigned_at = timezone.now()
            order.save()
            assigned_count += 1
            
            print(f"Auto-assigned order #{order.order_id} to {available_washer.full_name}")
        else:
            # No more available washers
            break
    
    return assigned_count


def notify_client_order_assigned(order):
    """
    Send notification to client when their order is assigned.
    Can be extended to send email/SMS notifications.
    """
    # TODO: Implement email/SMS notification
    print(f"Notification: Order #{order.order_id} assigned to {order.washer.full_name} for {order.client.email}")
    pass
