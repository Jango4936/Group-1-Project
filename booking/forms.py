# booking/forms.py

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm # use django builtin usercreation form for user authentications
from django.contrib.auth.models import User
from django import forms
import datetime

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


class ShopRegisterForm(UserCreationForm):

    shop_name = forms.CharField(max_length=100)
    opening_hours = forms.TimeField(label="Opening Time", widget=forms.TimeInput(attrs={"type": "time", "step": 60}))
    closing_hours = forms.TimeField(label="Closing Time",widget=forms.TimeInput(attrs={"type": "time", "step": 60}))
    address = forms.CharField(max_length=500)

    # create forms
    class Meta(UserCreationForm.Meta):
        model  = User
        fields = ["shop_name", "password1", "password2", "address", "opening_hours", "closing_hours"]