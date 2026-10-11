"""URL patterns for dashboard app."""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.EmployeeDashboardView.as_view(), name='employee_dashboard'),
]
