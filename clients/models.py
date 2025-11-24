from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
import uuid

# Create your models here.
class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Password hashing is handled in the view, not here
        super().save(*args, **kwargs)
    class Meta:
        # Link this model to your existing 'clients' table
        db_table = 'clients'

    def __str__(self):
        return self.email

class PasswordResetToken(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # Token expires after 1 hour
        expiry_time = self.created_at + timezone.timedelta(hours=1)
        return not self.is_used and timezone.now() < expiry_time

    class Meta:
        db_table = 'password_reset_tokens'

class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('motorcycle', 'Motorcycle'),
        ('other', 'Other'),
    ]
    
    vehicle_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='vehicles')
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    license_plate = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default='sedan')
    notes = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vehicles'
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.license_plate})"
    
    @property
    def full_name(self):
        year_str = f"{self.year} " if self.year else ""
        return f"{year_str}{self.make} {self.model}"

class WashOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    WASH_TYPE_CHOICES = [
        ('basic', 'Basic Wash'),
        ('premium', 'Premium Wash'),
        ('deluxe', 'Deluxe Wash'),
    ]

    order_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    washer = models.ForeignKey('washers.Washer', on_delete=models.SET_NULL, null=True, blank=True)
    wash_type = models.CharField(max_length=20, choices=WASH_TYPE_CHOICES, default='basic')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    client_notified = models.BooleanField(default=False)

    class Meta:
        db_table = 'wash_orders'

    def __str__(self):
        return f"Order #{self.order_id} - {self.vehicle} ({self.status})"
    
    def clean(self):
        """Validate that washer doesn't have multiple active orders"""
        from django.core.exceptions import ValidationError
        
        if self.washer and self.status in ['assigned', 'in_progress']:
            # Check if washer already has active orders (excluding current order)
            existing_orders = WashOrder.objects.filter(
                washer=self.washer,
                status__in=['assigned', 'in_progress']
            ).exclude(order_id=self.order_id)
            
            if existing_orders.exists():
                raise ValidationError(
                    f'Washer {self.washer.full_name} already has {existing_orders.count()} active order(s). '
                    f'A washer can only handle one order at a time.'
                )
    
    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.clean()
        super().save(*args, **kwargs)


class TimeSlot(models.Model):
    """Available time slots for appointments"""
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_capacity = models.PositiveIntegerField(default=3)  # How many appointments can be booked
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'time_slots'
        ordering = ['date', 'start_time']
        unique_together = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.date} {self.start_time} - {self.end_time}"
    
    @property
    def is_past(self):
        """Check if this time slot is in the past"""
        from django.utils import timezone
        from datetime import datetime
        
        now = timezone.now()
        slot_datetime = datetime.combine(self.date, self.start_time)
        
        # Make timezone aware if needed
        if timezone.is_naive(slot_datetime):
            slot_datetime = timezone.make_aware(slot_datetime)
        
        return slot_datetime < now
    
    @property
    def is_available(self):
        """Check if this time slot has available capacity"""
        if self.is_past or not self.is_active:
            return False
        
        booked_count = self.appointments.filter(is_cancelled=False).count()
        return booked_count < self.max_capacity
    
    @property
    def available_spots(self):
        """Get number of available spots"""
        booked_count = self.appointments.filter(is_cancelled=False).count()
        return max(0, self.max_capacity - booked_count)
    
    @property
    def booking_count(self):
        """Get current booking count"""
        return self.appointments.filter(is_cancelled=False).count()


class Appointment(models.Model):
    """Scheduled appointments for car wash services"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='appointments')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='appointments')
    wash_order = models.OneToOneField(WashOrder, on_delete=models.CASCADE, null=True, blank=True)
    
    # Appointment details
    wash_type = models.CharField(max_length=20, choices=WashOrder.WASH_TYPE_CHOICES, default='basic')
    special_instructions = models.TextField(blank=True)
    
    # Status tracking
    is_confirmed = models.BooleanField(default=True)
    is_cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointments'
        ordering = ['time_slot__date', 'time_slot__start_time']
    
    def __str__(self):
        return f"{self.client.first_name} - {self.time_slot} - {self.vehicle}"
    
    @property
    def appointment_datetime(self):
        """Get the full datetime of the appointment"""
        from django.utils import timezone
        return timezone.datetime.combine(self.time_slot.date, self.time_slot.start_time)
    
    def cancel_appointment(self, reason=""):
        """Cancel this appointment and free up the slot"""
        self.is_cancelled = True
        self.cancellation_reason = reason
        self.cancelled_at = timezone.now()
        self.save()
        
        # Cancel associated wash order if exists
        if self.wash_order:
            self.wash_order.status = 'cancelled'
            self.wash_order.save()
    
    def create_wash_order(self):
        """Create a wash order from this appointment"""
        if not self.wash_order:
            try:
                # Set price based on wash type
                prices = {
                    'basic': 15.00,
                    'premium': 25.00,
                    'deluxe': 35.00
                }
                
                print(f"DEBUG: Creating wash order for appointment {self.id}")
                print(f"DEBUG: Client: {self.client}, Vehicle: {self.vehicle}")
                print(f"DEBUG: Wash type: {self.wash_type}, Price: {prices.get(self.wash_type, 15.00)}")
                
                order = WashOrder.objects.create(
                    client=self.client,
                    vehicle=self.vehicle,
                    wash_type=self.wash_type,
                    price=prices.get(self.wash_type, 15.00),
                    notes=self.special_instructions,
                    status='pending'  # New status for scheduled orders
                )
                
                print(f"DEBUG: Wash order created successfully: {order.order_id}")
                
                self.wash_order = order
                self.save()
                return order
            except Exception as e:
                print(f"ERROR: Failed to create wash order for appointment {self.id}: {e}")
                raise e
        return self.wash_order


class Review(models.Model):
    """Client reviews for completed wash orders"""
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    review_id = models.AutoField(primary_key=True)
    job_id = models.IntegerField()  # Reference to order_id
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reviews')
    wash_order = models.OneToOneField(WashOrder, on_delete=models.CASCADE, related_name='review')
    washer = models.ForeignKey('washers.Washer', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for Order #{self.wash_order.order_id} - {self.rating} stars"