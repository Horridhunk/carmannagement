# clients/forms.py
from django import forms
from .models import Client, Vehicle, WashOrder, Appointment, TimeSlot
from django.utils import timezone
from django.db import models

class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = Client
        fields = ['email', 'first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number (optional)'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-input'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not Client.objects.filter(email=email).exists():
            raise forms.ValidationError("No account found with this email address.")
        return email

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New Password',
            'class': 'form-input'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm New Password',
            'class': 'form-input'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['make', 'model', 'year', 'color', 'license_plate', 'vehicle_type', 'notes']
        widgets = {
            'make': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Toyota, Honda, Ford'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Camry, Civic, F-150'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2020',
                'min': 1900,
                'max': 2030
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Red, Blue, White'
            }),
            'license_plate': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., ABC-1234',
                'style': 'text-transform: uppercase;'
            }),
            'vehicle_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special notes about your vehicle (optional)'
            }),
        }

    def clean_license_plate(self):
        license_plate = self.cleaned_data.get('license_plate')
        if license_plate:
            license_plate = license_plate.upper().strip()
            # Check if license plate already exists (excluding current instance if editing)
            existing = Vehicle.objects.filter(license_plate=license_plate)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("A vehicle with this license plate already exists.")
        return license_plate

class WashOrderForm(forms.ModelForm):
    class Meta:
        model = WashOrder
        fields = ['vehicle', 'wash_type', 'notes']
        widgets = {
            'vehicle': forms.Select(attrs={
                'class': 'form-control'
            }),
            'wash_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special instructions for the washer (optional)'
            }),
        }

    def __init__(self, client=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if client:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(client=client)


class AppointmentForm(forms.ModelForm):
    """Form for booking appointments with time slots"""
    
    class Meta:
        model = Appointment
        fields = ['vehicle', 'time_slot', 'wash_type', 'special_instructions']
        widgets = {
            'vehicle': forms.Select(attrs={
                'class': 'form-control'
            }),
            'time_slot': forms.Select(attrs={
                'class': 'form-control'
            }),
            'wash_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special instructions or requests (optional)'
            }),
        }

    def __init__(self, client=None, selected_date=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if client:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(client=client)
        
        # Filter time slots to show only available ones for the selected date
        if selected_date:
            from django.utils import timezone
            from datetime import datetime
            
            # Convert string date to date object if needed
            if isinstance(selected_date, str):
                selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            
            # Get all time slots for the date and filter manually
            all_slots = TimeSlot.objects.filter(
                date=selected_date,
                is_active=True
            )
            
            # Filter out fully booked slots
            available_slot_ids = []
            for slot in all_slots:
                booked_count = slot.appointments.filter(is_cancelled=False).count()
                if booked_count < slot.max_capacity:
                    available_slot_ids.append(slot.id)
            
            available_slots = TimeSlot.objects.filter(id__in=available_slot_ids)
            
            self.fields['time_slot'].queryset = available_slots
            self.fields['time_slot'].empty_label = "Select a time slot"
        else:
            # Show next 7 days of available slots
            from django.utils import timezone
            from datetime import timedelta
            
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=7)
            
            self.fields['time_slot'].queryset = TimeSlot.objects.filter(
                date__range=[start_date, end_date],
                is_active=True
            )

    def clean_time_slot(self):
        time_slot = self.cleaned_data.get('time_slot')
        
        if time_slot:
            if time_slot.is_past:
                raise forms.ValidationError("Cannot book appointments for past time slots.")
            
            if not time_slot.is_available:
                raise forms.ValidationError("This time slot is fully booked.")
        
        return time_slot


class TimeSlotSelectionForm(forms.Form):
    """Form for selecting date to view available time slots"""
    
    selected_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().isoformat()
        }),
        initial=timezone.now().date
    )
    
    def clean_selected_date(self):
        selected_date = self.cleaned_data.get('selected_date')
        
        if selected_date:
            from django.utils import timezone
            if selected_date < timezone.now().date():
                raise forms.ValidationError("Cannot select past dates.")
        
        return selected_date
