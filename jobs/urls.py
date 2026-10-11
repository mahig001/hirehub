from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.JobListView.as_view(), name='list'),
    path('create/', views.JobCreateView.as_view(), name='create'),
    path('my-jobs/', views.MyJobsListView.as_view(), name='my_jobs'),
    path('<slug:slug>/', views.JobDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.JobUpdateView.as_view(), name='update'),
]
