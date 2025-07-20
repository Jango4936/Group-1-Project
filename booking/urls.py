# booking/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.home, name='home'),
    path('schedule/', views.ScheduleAppointment.as_view(), name='schedule'),
    path('confirm/', views.confirm, name='confirm'),
    path('appointments/', views.AppointmentList.as_view(), name='appointments'),
    path('appointments/<int:pk>/delete/', views.AppointmentDelete.as_view(), name='appointment-delete'),

    # Shop login/register urls
    path('shop_register/', views.ShopRegister, name = "shop_register"),
    path('shop_register/confirmed/', views.shopRegConfirmed, name = "shop_registered"),
    path("shops/", include("django.contrib.auth.urls")),
    
    path('shop_homepage/', views.shopHomePage, name='shop_homepage'),
    
]
