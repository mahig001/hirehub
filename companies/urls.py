from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('create/', views.CompanyCreateView.as_view(), name='create'),
    path('list/', views.CompanyListView.as_view(), name='list'),
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/add/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    path('<slug:slug>/', views.CompanyDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.CompanyUpdateView.as_view(), name='update'),
]
