# Doxygen Comment Stubs for the Booking Django App
These are copy-paste ready docstrings that Doxygen (with doxypypy) will render.

## Models (booking/models.py)

Add these triple-quoted docstrings **immediately under** each class / method definition.

```python
class Shop(models.Model):
    """
    @brief Business owner profile and booking configuration.
    Stores the shop's name, slug, owner (Django User), phone, and working hours.
    @details
      - Unique, case-insensitive `name` is enforced via a DB constraint.
      - `slug` is auto-generated from `name` if not provided.
      - Includes open/close times and days the shop accepts appointments.

    @note Use `owner.shop` reverse relation to get a user's shop.
    """
    # fields...
    def save(self, *args, **kwargs):
        """
        @brief Ensure a unique slug before saving.
        @return None
        @post The `slug` field is set from `name` using `slugify`, with a numeric suffix if needed.
        """
        # implementation...
```

```python
class Client(models.Model):
    """
    @brief A customer who books appointments with a Shop.
    @details Stores contact information (name, phone, email) and optional notes.
    """
    def __str__(self):
        """@brief Human-readable identifier used in admin and templates."""
```

```python
class Appointment(models.Model):
    """
    @brief A scheduled service between a Client and a Shop.
    @details
      - `start_time`: timezone-aware datetime for the appointment start
      - `duration`: `datetime.timedelta`, defaults to 30 minutes
      - `status`: one of {"Confirmed","Completed","Cancelled"}
    @invariant duration.total_seconds() > 0
    """
    def __str__(self):
        """@brief 'Client @ start_time' for table listings and admin."""
```

## Forms (booking/forms.py)

```python
class AppointmentForm(forms.ModelForm):
    """
    @brief Validates and creates `Appointment` instances.
    @param shop Shop The shop context used to validate times/business days.
    @warning Raises `forms.ValidationError` if the requested slot is invalid.
    """
    def clean(self):
        """
        @brief Cross-field validations for appointment time and conflicts.
        @exception forms.ValidationError on overlaps, closed days, or past times.
        @return dict Cleaned data.
        """
```

```python
class ShopRegisterForm(forms.ModelForm):
    """
    @brief Registration form for creating a `Shop` linked to the logged-in user.
    """
    def clean_shop_name(self):
        """
        @brief Enforce case-insensitive uniqueness of `name`.
        @return str Normalized name.
        """
```

## Views (booking/views.py)

```python
class ScheduleAppointment(View):
    """
    @brief Public booking page to select a date/time and submit an appointment.
    @details GET renders the booking form; POST validates and creates the appointment.
    """
    def get(self, request, *args, **kwargs):
        """@brief Render available slots and the booking form. @return HttpResponse"""
    def post(self, request, *args, **kwargs):
        """
        @brief Create an appointment from POSTed data.
        @param request HttpRequest Incoming request with form fields.
        @return HttpResponse Redirect on success; re-render with errors otherwise.
        """
```

```python
class shopAppointmentsManage(LoginRequiredMixin, ListView):
    """
    @brief Staff dashboard for viewing and managing appointments.
    @details Filters by status and date; supports mark-complete/confirm/cancel actions.
    """
    def get_queryset(self):
        """@brief Return appointments for the logged-in shop owner. @return QuerySet"""
```

## URLs (booking/urls.py)

```python
#: @brief URL patterns for the booking application.
urlpatterns = [
    # ...
    path("appointments_manage/<int:pk>/complete/", views.MarkCompleted.as_view(), name="appointment-complete"),
    # ...
]
```
