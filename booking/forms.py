# booking/forms.py

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm # use django builtin usercreation form for user authentications
from django.contrib.auth.models import User
from django import forms
from django.db import transaction, IntegrityError
import datetime

from .models import Appointment, Client, Shop
from .models import DAYS_OF_WEEK

class AppointmentForm(forms.Form):
    # either pick an existing client or enter new info
    name       = forms.CharField(max_length=100)
    email      = forms.EmailField()
    phone      = forms.CharField(max_length=20)
    shop       = forms.ModelChoiceField(queryset=Shop.objects.all(), required=False)
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )



    # durations
    DURATION_CHOICES = [
        (30,  "30 minutes"),
        (45,  "45 minutes"),
        (60,  "1 hour"),
        (120, "2 hours"),
    ]

    duration = forms.TypedChoiceField(
        label="Duration",
        choices=DURATION_CHOICES,                 # value = minutes
        coerce=lambda m: datetime.timedelta(minutes=int(m)),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    note = forms.CharField(widget=forms.Textarea)


    def clean(self):
        cleaned = super().clean()
        shop = cleaned.get("shop")
        start_dt = cleaned.get("start_time")

        if shop and start_dt:
            # map codes (e.g. 'mon') → weekday ints (Mon=0 … Sun=6)
            code_to_int = { code: idx for idx, (code, _) in enumerate(DAYS_OF_WEEK) }
            open_day = code_to_int[shop.opening_day]
            close_day = code_to_int[shop.closing_day]
            wd = start_dt.weekday()

            # Day‐of‐week check 
            if open_day <= close_day:
                valid_day = (open_day <= wd <= close_day)
            else:
                valid_day = (wd >= open_day or wd <= close_day)

            if not valid_day:
                raise forms.ValidationError(
                    "⚠ The shop is closed on that day. Please pick another date."
                )

            # Time‐of‐day check
            t = start_dt.time()
            if t < shop.opening_hours or t > shop.closing_hours:
                raise forms.ValidationError(
                    "⚠ The shop is closed at that time. Please pick a time between "
                    f"{shop.opening_hours:%H:%M} and {shop.closing_hours:%H:%M}."
                )

        return cleaned


class ShopRegisterForm(UserCreationForm):

    shop_name = forms.CharField(max_length=100)
    opening_hours = forms.TimeField(label="Opening Time", widget=forms.TimeInput(attrs={"type": "time", "step": 60}))
    closing_hours = forms.TimeField(label="Closing Time",widget=forms.TimeInput(attrs={"type": "time", "step": 60}))
    address = forms.CharField(max_length=500)
    phone      = forms.CharField(max_length=20)
    description = forms.CharField(max_length=500)
    opening_day   = forms.ChoiceField(
                       choices=DAYS_OF_WEEK,
                       label="Opening Day",
                   )
    closing_day   = forms.ChoiceField(
                       choices=DAYS_OF_WEEK,
                       label="Closing Day",
                   )

    # create forms
    class Meta(UserCreationForm.Meta):
        model  = User
        fields = ["username", "shop_name", "password1", "password2", "phone", "address", "description", "opening_hours", "closing_hours","opening_day", "closing_day"]



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
                    phone=self.cleaned_data["phone"],
                    address=self.cleaned_data["address"],
                    description=self.cleaned_data["description"],
                    opening_hours=self.cleaned_data["opening_hours"],
                    closing_hours=self.cleaned_data["closing_hours"],
                    opening_day=self.cleaned_data["opening_day"],
                    closing_day=self.cleaned_data["closing_day"],
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