# booking/views.py

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from .forms import AppointmentForm, ShopRegisterForm
from .models import Client, Appointment, Shop

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
            )
            return redirect('booking:confirm')
        return render(request, self.template_name, {'form': form})
def confirm(request):
    return render(request, 'confirm.html')
# booking/views.py

class AppointmentList(ListView):
    model = Appointment
    template_name = 'appointments.html'      # your template
    context_object_name = 'appointments'     # in template use “appointments”
    ordering = ['start_time']               # optional: sort by time



# create new shop
def ShopRegister(response):
    if response.method == "POST":
        form = ShopRegisterForm(response.POST)
        if form.is_valid():
            form.save()
            return redirect("/shop_register/confirmed/")
    else:
        form = ShopRegisterForm
    
    return render(response, "registrations/shop_register.html", {"form":form})

# new shop confirmation
def shopRegConfirmed(request):
    return render(request, 'registrations/confirm.html')
