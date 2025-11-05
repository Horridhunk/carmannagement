from django.db import models
from .client import Client

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