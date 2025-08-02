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
    path('shop_settings/', views.shopSettingsView.as_view(), name='shop_settings'),
    
    # Shop Management
    path('shop_homepage/', views.shopHomePage.as_view(), name='shop_homepage'),
    path('appointments_manage/', views.shopAppointmentsManage.as_view(), name='appointments_manage'),
    path('appointments_manage/<int:pk>/delete/', views.shopsAppointmentDelete.as_view(), name='shops-appointment-delete'),
    path("appointments_manage/<int:pk>/complete/", views.MarkCompleted.as_view(),name="appointment-complete"),
    path("appointments_manage/<int:pk>/confirmed/", views.MarkConfirmed.as_view(),name="appointment-confirmed"),
    path("appointments_manage/<int:pk>/cancelled/", views.MarkCancelled.as_view(),name="appointment-cancelled"),
]
