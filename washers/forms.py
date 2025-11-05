from django import forms
from .models import Washer
import re

class WasherSignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-control'
        })
    )
    phone = forms.CharField(
        required=True,
        max_length=15,  # Allow for spaces during input
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone Number (e.g., 0711223344 or 0123456789)',
            'class': 'form-control',
            'title': 'Phone number must start with 01 or 07 and contain exactly 10 digits'
        })
    )

    class Meta:
        model = Washer
        fields = ['email', 'first_name', 'last_name', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email Address',
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First Name',
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last Name',
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        
        # Store original for debugging
        original_phone = phone
        
        # Remove any spaces, dashes, or other non-digit characters except the leading digits
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Debug info
        print(f"Phone validation debug:")
        print(f"  Original: '{original_phone}'")
        print(f"  Cleaned: '{phone}'")
        print(f"  Length: {len(phone)}")
        print(f"  Starts with 01/07: {phone.startswith('01') or phone.startswith('07')}")
        
        # Check if phone number matches the pattern: starts with 01 or 07 and has exactly 10 digits
        if len(phone) != 10:
            raise forms.ValidationError(
                f"Phone number must be exactly 10 digits. You entered {len(phone)} digits: '{phone}'"
            )
            
        if not (phone.startswith('01') or phone.startswith('07')):
            raise forms.ValidationError(
                f"Phone number must start with 01 or 07. Your number starts with: '{phone[:2]}'"
            )
            
        if not phone.isdigit():
            raise forms.ValidationError(
                f"Phone number must contain only digits. Invalid characters found in: '{phone}'"
            )
        
        # Check if phone number already exists
        if Washer.objects.filter(phone=phone).exists():
            raise forms.ValidationError("A washer with this phone number already exists.")
        
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Washer.objects.filter(email=email).exists():
            raise forms.ValidationError("A washer with this email already exists.")
        return email


class AdminAddWasherForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control',
            'required': True
        }),
        help_text="Enter a secure password for the new staff member"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-control',
            'required': True
        }),
        help_text="Re-enter the password to confirm"
    )
    phone = forms.CharField(
        required=True,
        max_length=15,
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone Number (e.g., 0711223344)',
            'class': 'form-control',
            'title': 'Phone number must start with 01 or 07 and contain exactly 10 digits'
        }),
        help_text="Phone number starting with 01 or 07 (10 digits total)"
    )
    hourly_rate = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Hourly Rate (optional)',
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        help_text="Optional: Set hourly rate for this staff member"
    )

    class Meta:
        model = Washer
        fields = ['email', 'first_name', 'last_name', 'phone', 'hourly_rate', 'is_available', 'status']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email Address',
                'class': 'form-control',
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First Name',
                'class': 'form-control',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last Name',
                'class': 'form-control',
                'required': True
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        help_texts = {
            'email': 'Enter a valid email address for the staff member',
            'first_name': 'Staff member\'s first name',
            'last_name': 'Staff member\'s last name',
            'is_available': 'Check if the staff member is available for work',
            'status': 'Set the current status of the staff member'
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        
        # Remove any spaces, dashes, or other non-digit characters
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check if phone number matches the pattern: starts with 01 or 07 and has exactly 10 digits
        if len(phone) != 10:
            raise forms.ValidationError(
                f"Phone number must be exactly 10 digits. You entered {len(phone)} digits."
            )
            
        if not (phone.startswith('01') or phone.startswith('07')):
            raise forms.ValidationError(
                "Phone number must start with 01 or 07."
            )
            
        if not phone.isdigit():
            raise forms.ValidationError(
                "Phone number must contain only digits."
            )
        
        # Check if phone number already exists
        if Washer.objects.filter(phone=phone).exists():
            raise forms.ValidationError("A staff member with this phone number already exists.")
        
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Washer.objects.filter(email=email).exists():
            raise forms.ValidationError("A staff member with this email already exists.")
        return email

class WasherProfileForm(forms.ModelForm):
    """Form for washers to edit their profile information"""
    
    class Meta:
        model = Washer
        fields = ['first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        
        # Remove any spaces, dashes, or other non-digit characters
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check if phone number matches the pattern: starts with 01 or 07 and has exactly 10 digits
        if len(phone) != 10:
            raise forms.ValidationError(
                f"Phone number must be exactly 10 digits. You entered {len(phone)} digits."
            )
            
        if not (phone.startswith('01') or phone.startswith('07')):
            raise forms.ValidationError(
                "Phone number must start with 01 or 07."
            )
            
        if not phone.isdigit():
            raise forms.ValidationError(
                "Phone number must contain only digits."
            )
        
        # Check if phone number already exists (excluding current user)
        if self.instance and self.instance.pk:
            if Washer.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A washer with this phone number already exists.")
        else:
            if Washer.objects.filter(phone=phone).exists():
                raise forms.ValidationError("A washer with this phone number already exists.")
        
        return phone


class WasherPasswordChangeForm(forms.Form):
    """Form for washers to change their password"""
    
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current Password',
            'required': True
        }),
        help_text="Enter your current password",
        required=True
    )
    
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password',
            'required': True
        }),
        help_text="Enter your new password (minimum 8 characters)",
        required=True
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password',
            'required': True
        }),
        help_text="Re-enter your new password",
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.washer = kwargs.pop('washer', None)
        print(f"WasherPasswordChangeForm initialized with washer: {self.washer}")
        print(f"Args: {args}, Kwargs: {kwargs}")
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        print(f"Cleaning current_password: '{current_password}'")
        
        if not current_password:
            print("Current password is empty!")
            raise forms.ValidationError("Current password is required.")
            
        if not self.washer:
            print("No washer instance!")
            raise forms.ValidationError("No washer instance provided.")
            
        from django.contrib.auth.hashers import check_password
        
        print(f"Checking password against hash: {self.washer.password_hash[:20]}...")
        password_valid = check_password(current_password, self.washer.password_hash)
        print(f"Password check result: {password_valid}")
        
        if not password_valid:
            raise forms.ValidationError("Current password is incorrect.")
        
        return current_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if not new_password:
            raise forms.ValidationError("New password is required.")
        if len(new_password) < 8:
            raise forms.ValidationError("New password must be at least 8 characters long.")
        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        print(f"Form clean method - new_password: {bool(new_password)}, confirm_password: {bool(confirm_password)}")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("New passwords do not match.")

        return cleaned_data


class AdminEditWasherForm(forms.ModelForm):
    """Form for admin to edit existing washer/staff member"""
    
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New Password (leave blank to keep current)',
            'class': 'form-control'
        }),
        help_text="Leave blank to keep current password"
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm New Password',
            'class': 'form-control'
        }),
        help_text="Re-enter the new password to confirm"
    )
    phone = forms.CharField(
        required=True,
        max_length=15,
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone Number (e.g., 0711223344)',
            'class': 'form-control',
            'title': 'Phone number must start with 01 or 07 and contain exactly 10 digits'
        }),
        help_text="Phone number starting with 01 or 07 (10 digits total)"
    )
    hourly_rate = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Hourly Rate (optional)',
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        help_text="Optional: Set hourly rate for this staff member"
    )

    class Meta:
        model = Washer
        fields = ['email', 'first_name', 'last_name', 'phone', 'hourly_rate', 'is_available', 'status']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email Address',
                'class': 'form-control',
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First Name',
                'class': 'form-control',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last Name',
                'class': 'form-control',
                'required': True
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        help_texts = {
            'email': 'Enter a valid email address for the staff member',
            'first_name': 'Staff member\'s first name',
            'last_name': 'Staff member\'s last name',
            'is_available': 'Check if the staff member is available for work',
            'status': 'Set the current status of the staff member'
        }

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # Only validate password if it's being changed
        if new_password or confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("New passwords do not match.")
            
            if new_password and len(new_password) < 8:
                raise forms.ValidationError("New password must be at least 8 characters long.")

        return cleaned_data

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        
        # Remove any spaces, dashes, or other non-digit characters
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check if phone number matches the pattern: starts with 01 or 07 and has exactly 10 digits
        if len(phone) != 10:
            raise forms.ValidationError(
                f"Phone number must be exactly 10 digits. You entered {len(phone)} digits."
            )
            
        if not (phone.startswith('01') or phone.startswith('07')):
            raise forms.ValidationError(
                "Phone number must start with 01 or 07."
            )
            
        if not phone.isdigit():
            raise forms.ValidationError(
                "Phone number must contain only digits."
            )
        
        # Check if phone number already exists (excluding current instance)
        if self.instance and self.instance.pk:
            if Washer.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A staff member with this phone number already exists.")
        else:
            if Washer.objects.filter(phone=phone).exists():
                raise forms.ValidationError("A staff member with this phone number already exists.")
        
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if email already exists (excluding current instance)
        if self.instance and self.instance.pk:
            if Washer.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A staff member with this email already exists.")
        else:
            if Washer.objects.filter(email=email).exists():
                raise forms.ValidationError("A staff member with this email already exists.")
        
        return email