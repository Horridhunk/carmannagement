from django.contrib import admin
from .models import Client, PasswordResetToken, Vehicle, WashOrder, TimeSlot, Appointment

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'date_created')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('date_created',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'make', 'model', 'year', 'client', 'date_added')
    search_fields = ('license_plate', 'make', 'model')
    list_filter = ('vehicle_type', 'date_added')

@admin.register(WashOrder)
class WashOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'client', 'vehicle', 'wash_type', 'status', 'price', 'created_at')
    search_fields = ('order_id', 'client__email', 'vehicle__license_plate')
    list_filter = ('status', 'wash_type', 'created_at')
    readonly_fields = ('order_id', 'created_at', 'assigned_at', 'started_at', 'completed_at')

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time', 'max_capacity', 'booking_count', 'is_active')
    search_fields = ('date',)
    list_filter = ('date', 'is_active')
    date_hierarchy = 'date'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'vehicle', 'time_slot', 'wash_type', 'is_confirmed', 'is_cancelled', 'created_at')
    search_fields = ('client__email', 'vehicle__license_plate')
    list_filter = ('is_confirmed', 'is_cancelled', 'wash_type', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'cancelled_at')

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('client', 'token', 'created_at', 'is_used')
    search_fields = ('client__email',)
    list_filter = ('is_used', 'created_at')
    readonly_fields = ('token', 'created_at')
