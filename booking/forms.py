# booking/forms.py

from django import forms
from .models import Appointment, Client, Shop

class AppointmentForm(forms.Form):
    # either pick an existing client or enter new info
    name       = forms.CharField(max_length=100)
    email      = forms.EmailField()
    phone      = forms.CharField(max_length=20)
    shop       = forms.ModelChoiceField(queryset=Shop.objects.all(), required=False)
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
