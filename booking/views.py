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
from .forms import AppointmentForm, ShopRegisterForm
from .models import Client, Appointment, Shop, DAYS_OF_WEEK

def home(request):
    return render(request, 'home.html')

class ScheduleAppointment(View):
    template_name = 'schedule.html'

    def get(self, request):
        form = AppointmentForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # get or create client
            client, created = Client.objects.get_or_create(
                email=form.cleaned_data['email'],
                defaults={
                    'name': form.cleaned_data['name'],
                    'phone': form.cleaned_data['phone']
                }
            )
            # if existing client but phone/name changed, you could update them here

            # create appointment
            Appointment.objects.create(
                client=client,
                shop=form.cleaned_data['shop'],
                start_time=form.cleaned_data['start_time'],
                duration=form.cleaned_data['duration'],
            )
            return redirect('booking:confirm')
        return render(request, self.template_name, {'form': form})
def confirm(request):
    return render(request, 'confirm.html')
# booking/views.py

class shopSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "shops/shop_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import DAYS_OF_WEEK
        context["days_of_week"] = DAYS_OF_WEEK
        return context
    
    def post(self, request, *args, **kwargs):
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
    template_name = "shops/appointments_manage.html"

    def get_queryset(self):
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
        return HttpResponseNotAllowed(["POST"])
    
class MarkCompleted(UpdateShopAppointmentStatus):
    status_value = "Completed"

class MarkConfirmed(UpdateShopAppointmentStatus):
    status_value = "Confirmed"

class MarkCancelled(UpdateShopAppointmentStatus):
    status_value = "Cancelled"