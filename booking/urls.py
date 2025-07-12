# booking/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.home, name='home'),
    path('schedule/', views.ScheduleAppointment.as_view(), name='schedule'),
    path('confirm/', views.confirm, name='confirm'),
    path('appointments/', views.AppointmentList.as_view(), name='appointments'),

    # Shop login/register urls
    path('shop_register/', views.ShopRegister, name = "shop_register"),
    
]
