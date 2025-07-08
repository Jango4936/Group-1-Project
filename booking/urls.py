# booking/urls.py

from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.home, name='home'),
    path('schedule/', views.ScheduleAppointment.as_view(), name='schedule'),
    path('confirm/', views.confirm, name='confirm'),
    path('appointments/', views.AppointmentList.as_view(), name='appointments'),
]
