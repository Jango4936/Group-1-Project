# booking/forms.py

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm # use django builtin usercreation form for user authentications
from django.contrib.auth.models import User
from django import forms
from django.db import transaction, IntegrityError
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
        fields = ["username", "shop_name", "password1", "password2", "address", "opening_hours", "closing_hours"]



    def clean_shop_name(self):
        name = self.cleaned_data["shop_name"]
        if Shop.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("That shop name is already taken.")
        return name


    def save(self, commit=True):
        
        user = super().save(commit=commit)

        try:
            with transaction.atomic():
                Shop.objects.create(
                    owner=user,
                    name=self.cleaned_data["shop_name"],
                    address=self.cleaned_data["address"],
                    opening_hours=self.cleaned_data["opening_hours"],
                    closing_hours=self.cleaned_data["closing_hours"],
                )
        except IntegrityError:                 
            self.add_error(
                "shop_name",
                "That shop name was just registered by someone else. "
                "Please pick another one.",
            )
            user.delete()                      
            raise forms.ValidationError("duplicate shop")

        return user