from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Washer(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_break', 'On Break'),
    ]
    
    washer_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=False, null=False)
    is_available = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_hired = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        db_table = 'washers'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def has_active_orders(self):
        """Check if washer has any active orders (assigned or in_progress)"""
        try:
            from clients.models import WashOrder
            return WashOrder.objects.filter(
                washer=self,
                status__in=['assigned', 'in_progress']
            ).exists()
        except:
            return False
    
    @property
    def active_orders_count(self):
        """Get count of active orders for this washer"""
        try:
            from clients.models import WashOrder
            return WashOrder.objects.filter(
                washer=self,
                status__in=['assigned', 'in_progress']
            ).count()
        except:
            return 0
    
    @property
    def is_truly_available(self):
        """Check if washer is available and has no active orders"""
        return self.is_available and not self.has_active_orders
