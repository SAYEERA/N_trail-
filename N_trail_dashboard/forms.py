from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Location

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['Location_ID', 'State', 'County', 'Owner', 'Latitude', 'Longitude', 'Contact', 'MetaData']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
