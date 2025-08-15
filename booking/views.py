# booking/views.py
import datetime
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.db import transaction
from django.db.models import F, ExpressionWrapper, DateTimeField
from django import forms
from .forms import AppointmentForm, ShopRegisterForm
from .models import Client, Appointment, Shop, DAYS_OF_WEEK

def home(request):
    return render(request, 'home.html')

class ScheduleAppointment(View):
    """
    @brief Public booking page to select a date/time and submit an appointment.
    @details GET renders the booking form; POST validates and creates the appointment.
    """
    template_name = 'schedule.html'

    def get(self, request):
        """@brief Render available slots and the booking form. @return HttpResponse"""
        form = AppointmentForm()
        # generic page must choose a shop
        form.fields['shop'].required = True
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        @brief Create an appointment from POSTed data.
        @param request HttpRequest Incoming request with form fields.
        @return HttpResponse Redirect on success; re-render with errors otherwise.
        """
        form = AppointmentForm(request.POST)
        # generic page must choose a shop
        form.fields['shop'].required = True

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        shop     = form.cleaned_data.get('shop')
        start_dt = form.cleaned_data['start_time']
        duration = form.cleaned_data['duration']
        end_dt   = start_dt + duration

        if not shop:
            form.add_error('shop', "Please choose a shop.")
            return render(request, self.template_name, {'form': form})

        # Optional defensive check (form may already enforce this)
        if (start_dt.time() < shop.opening_hours
            or end_dt.time() > shop.closing_hours
            or start_dt.date() != end_dt.date()):
            form.add_error('start_time', "⚠ Appointment must fit within business hours and not span days.")
            return render(request, self.template_name, {'form': form})

        blocking_statuses = ["Pending", "Confirmed"]

        from django.db import transaction
        from django.db.models import F, ExpressionWrapper, DateTimeField

        with transaction.atomic():
            conflict = (
                Appointment.objects
                .filter(shop=shop, status__in=blocking_statuses)
                .annotate(existing_end=ExpressionWrapper(
                    F("start_time") + F("duration"),
                    output_field=DateTimeField()
                ))
                .filter(
                    start_time__lt=end_dt,     # existing starts before new ends
                    existing_end__gt=start_dt  # existing ends after new starts
                )
                .exists()
            )
            if conflict:
                form.add_error('start_time', "⚠ That time overlaps another booking, please pick another time.")
                return render(request, self.template_name, {'form': form})

            # create/update client then create appt
            client, _ = Client.objects.get_or_create(
                email=form.cleaned_data['email'],
                defaults={'name': form.cleaned_data['name'], 'phone': form.cleaned_data['phone']}
            )
            if client.name != form.cleaned_data['name'] or client.phone != form.cleaned_data['phone']:
                client.name  = form.cleaned_data['name']
                client.phone = form.cleaned_data['phone']
                client.save(update_fields=['name', 'phone'])

            Appointment.objects.create(
                client=client,
                shop=shop,
                start_time=start_dt,
                duration=duration,
                note=form.cleaned_data['note'],
                status="Confirmed",
            )

        return redirect('booking:confirm')
def confirm(request):
    return render(request, 'confirm.html')


class shopSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "shops/shop_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import DAYS_OF_WEEK
        context["days_of_week"] = DAYS_OF_WEEK
        return context
    
    def post(self, request, *args, **kwargs):
        """
        @brief Create an appointment from POSTed data.
        @param request HttpRequest Incoming request with form fields.
        @return HttpResponse Redirect on success; re-render with errors otherwise.
        """
        shop = request.user.shop

        if "shop_name" in request.POST:
            shop.name = request.POST.get("shop_name")

        if "shop_address" in request.POST:
            shop.address = request.POST.get("shop_address")

        if "phone_number" in request.POST:
            shop.phone = request.POST.get("phone_number")

        if "opening_hours" in request.POST:
            shop.opening_hours = request.POST.get("opening_hours")

        if "closing_hours" in request.POST:
            shop.closing_hours = request.POST.get("closing_hours")

        if "opening_day" in request.POST:
            shop.opening_day = request.POST.get("opening_day")           

        if "closing_day" in request.POST:
            shop.closing_day = request.POST.get("closing_day") 

        if "shop_description" in request.POST:
            shop.description = request.POST.get("shop_description") 
        

        shop.save()
        messages.success(request, "Shop settings updated!")
        return redirect("booking:shop_settings")

def shop_settings_view(request):
    return render(request, "shops/shop_settings.html", {
        "days_of_week": DAYS_OF_WEEK
    })

class AppointmentList(ListView):
    model = Appointment
    template_name = 'appointments.html'      # your template
    context_object_name = 'appointments'     # in template use “appointments”
    ordering = ['start_time']               # optional: sort by time

class AppointmentDelete(DeleteView):
    model = Appointment
    template_name = 'appointment_confirm_delete.html'
    success_url = reverse_lazy('booking:appointments')

class shopsAppointmentDelete(AppointmentDelete):
    template_name = "shops/appointments_manage.html"
    success_url = reverse_lazy('booking:appointments_manage')





# create new shop
def ShopRegister(response):
    if response.method == "POST":
        form = ShopRegisterForm(response.POST)
        if form.is_valid():
            form.save()
            return redirect("/shop_register/confirmed/")
    else:
        form = ShopRegisterForm
    
    return render(response, "registration/shop_register.html", {"form":form})

# new shop confirmation
def shopRegConfirmed(request):
    return render(request, 'registration/confirm.html')



class shopHomePage(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'shops/shop_homepage.html'      
    context_object_name = 'appointments'    # in template use “appointments”
    ordering = ['start_time']               # optional: sort by time

    def get_queryset(self):
        """@brief Return appointments for the logged-in shop owner. @return QuerySet"""
        # If the user hasn't linked a shop yet → no data
        if not hasattr(self.request.user, "shop"):
            return Appointment.objects.none()

        return (
            Appointment.objects
            .filter(
                shop=self.request.user.shop    # only this shop
            )
            .select_related("client")          # fetch client in same query
            .order_by("start_time")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # only future/ongoing appointments
        ctx["future_appointments"] = ctx["appointments"].filter(
            start_time__gte=timezone.now()
        )
        # future confirmed appointment
        ctx["future_confirmed_appointments"] = ctx["future_appointments"].filter(
            status__iexact="confirmed"
        )

        # completed appointments
        completed = ctx["completed_appointments"]  = ctx["appointments"].filter(
            status__iexact="completed"
        )

        today          = timezone.localdate()                 
        start_of_week  = today - timedelta(days=today.weekday())  # Monday
        start_dt       = timezone.make_aware(datetime.datetime.combine(start_of_week, datetime.time.min))
        end_dt         = start_dt + timedelta(days=7)         # next Monday 00:00

        # completed appointment in current week
        ctx["completed_this_week"] = completed.filter(
            start_time__gte=start_dt,
            start_time__lt=end_dt
        )


        # quick‐stat badges
        ctx["total_count"]  = ctx["appointments"].count()
        ctx["future_count"] = ctx["future_appointments"].count()
        ctx["completed_count"] = ctx["completed_appointments"].count()
        ctx["completedThisWeek_count"] = ctx["completed_this_week"].count()
        ctx["future_confirmed_count"] = ctx["future_confirmed_appointments"].count()
        return ctx

# subclass of shophomepage
class shopAppointmentsManage(shopHomePage):
    """
    @brief Staff dashboard for viewing and managing appointments.
    @details Filters by status and date; supports mark-complete/confirm/cancel actions.
    """
    template_name = "shops/appointments_manage.html"

    def get_queryset(self):
        """@brief Return appointments for the logged-in shop owner. @return QuerySet"""
        qs = super().get_queryset()              # all of this shop’s appts
        g  = self.request.GET

        # --- search text ---
        q = g.get("q")
        if q:
            qs = qs.filter(
                Q(client__name__icontains=q) |
                Q(client__email__icontains=q) |
                Q(client__phone__icontains=q)
            )

        # --- status filter ---
        status = g.get("status")
        if status:
            qs = qs.filter(status__iexact=status)

        # --- date range filter ---
        rng = g.get("range")
        if rng == "today":
            qs = qs.filter(start_time__date=date.today())
        elif rng == "week":
            start = date.today() - timedelta(days=date.today().weekday())
            end   = start + timedelta(days=7)
            qs = qs.filter(start_time__date__gte=start, start_time__date__lt=end)
        elif rng == "month":
            start = date.today().replace(day=1)
            end   = (start + timedelta(days=32)).replace(day=1)
            qs = qs.filter(start_time__date__gte=start, start_time__date__lt=end)
        elif rng == "upcoming":
            qs = qs.filter(start_time__gte=timezone.now())

        # --- sorting ---
        sort = g.get("sort", "date_desc")
        sort_map = {
            "date_asc":  "start_time",
            "date_desc": "-start_time",
            "customer":  "client__name",
            "status":    "status",
        }
        qs = qs.order_by(sort_map.get(sort, "-start_time"))

        return qs
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return render(
                self.request,
                "shops/_appointments_list.html",   # partial containing only the list div
                context
            )
        return super().render_to_response(context, **response_kwargs)



# parent class for update appointment status
class UpdateShopAppointmentStatus(LoginRequiredMixin, View):
    status_value: str = None                # override
    success_url   = reverse_lazy("booking:appointments_manage")

    def post(self, request, pk, *args, **kwargs):
        """
        @brief Create an appointment from POSTed data.
        @param request HttpRequest Incoming request with form fields.
        @return HttpResponse Redirect on success; re-render with errors otherwise.
        """
        if self.status_value is None:
            return HttpResponseNotAllowed(["POST"])

        appt = get_object_or_404(
            Appointment,
            pk=pk,
            shop=request.user.shop,         # safety check
        )
        appt.status = self.status_value
        appt.save(update_fields=["status"])
        return redirect(self.success_url)

    # block GET for safety
    def get(self, *args, **kwargs):
        """@brief Render available slots and the booking form. @return HttpResponse"""
        return HttpResponseNotAllowed(["POST"])
    
class MarkCompleted(UpdateShopAppointmentStatus):
    status_value = "Completed"

class MarkConfirmed(UpdateShopAppointmentStatus):
    status_value = "Confirmed"

class MarkCancelled(UpdateShopAppointmentStatus):
    status_value = "Cancelled"


# Shop Appointment Schedule Page
class ShopAppointment(View):
    template_name = 'book_shop.html'

    def get(self, request, slug):
        """@brief Render available slots and the booking form. @return HttpResponse"""
        shop = get_object_or_404(Shop, slug=slug)
        form = AppointmentForm(initial={'shop': shop})
        form.fields['shop'].queryset = Shop.objects.filter(pk=shop.pk)
        form.fields['shop'].widget = forms.HiddenInput()
        return render(request, self.template_name, {'form': form, 'shop': shop})

    def post(self, request, slug):
        """
        @brief Create an appointment from POSTed data.
        @param request HttpRequest Incoming request with form fields.
        @return HttpResponse Redirect on success; re-render with errors otherwise.
        """
        shop = get_object_or_404(Shop, slug=slug)
        form = AppointmentForm(request.POST)

        # keep it tied to this shop & hidden on re-render
        form.fields['shop'].queryset = Shop.objects.filter(pk=shop.pk)
        form.fields['shop'].widget = forms.HiddenInput()

        if form.is_valid():
            
            # cleaned data
            start_dt  = form.cleaned_data['start_time']
            duration  = form.cleaned_data['duration']
            end_dt    = start_dt + duration

            # keep inside business hours & same day
            if start_dt.time() < shop.opening_hours or end_dt.time() > shop.closing_hours or start_dt.date() != end_dt.date():
                form.add_error('start_time',
                    "⚠ Appointment must fit within business hours and not span days.")
                return render(request, self.template_name, {'form': form, 'shop': shop})

            blocking_statuses = ["Pending", "Confirmed"]

            # Do the overlap check + create atomically to avoid races
            with transaction.atomic():
                conflict_exists = (
                    Appointment.objects
                    .filter(shop=shop, status__in=blocking_statuses)
                    .annotate(existing_end=ExpressionWrapper(
                        F("start_time") + F("duration"),
                        output_field=DateTimeField()
                    ))
                    .filter(
                        start_time__lt=end_dt,      # existing starts before new ends
                        existing_end__gt=start_dt   # existing ends after new starts
                    )
                    .exists()
                )
                if conflict_exists:
                    form.add_error('start_time', "⚠ That time overlaps another booking, please pick another time.")
                    return render(request, self.template_name, {'form': form, 'shop': shop})
            
            
            # get or create client
            client, _ = Client.objects.get_or_create(
                email=form.cleaned_data['email'],
                defaults={
                    'name':  form.cleaned_data['name'],
                    'phone': form.cleaned_data['phone'],
                }
            )
            # keep name/phone in sync if returning client
            if client.name != form.cleaned_data['name'] or client.phone != form.cleaned_data['phone']:
                client.name  = form.cleaned_data['name']
                client.phone = form.cleaned_data['phone']
                client.save(update_fields=['name', 'phone'])

            # create appointment bound to THIS shop
            Appointment.objects.create(
                client=client,
                shop=shop, 
                start_time=form.cleaned_data['start_time'],
                duration=form.cleaned_data['duration'],
                note=form.cleaned_data['note'],
                status="Confirmed",
            )
            return redirect('booking:confirm')

        # not valid: show errors (incl. your day/hour checks)
        return render(request, self.template_name, {'form': form, 'shop': shop})