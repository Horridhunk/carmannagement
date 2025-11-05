from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate


class AdminLoginForm(AuthenticationForm):
    """
    Custom login form for admin users only.
    No signup functionality - admins are created manually.
    """
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Admin Username'
        self.fields['password'].label = 'Password'
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Invalid username or password.",
                    code='invalid_login'
                )
            
            # Check if user is staff (admin)
            if not self.user_cache.is_staff:
                raise forms.ValidationError(
                    "Access denied. Admin privileges required.",
                    code='not_admin'
                )
                
        return self.cleaned_data