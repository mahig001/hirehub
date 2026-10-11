"""URL patterns for applications app."""
from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('jobs/<int:job_pk>/apply/', views.ApplyView.as_view(), name='apply'),
    path('<int:pk>/', views.ApplicationDetailView.as_view(), name='detail'),
    path('<int:pk>/withdraw/', views.WithdrawApplicationView.as_view(), name='withdraw'),
    path('my-applications/', views.MyApplicationsListView.as_view(), name='my_applications'),
    path('<int:pk>/timeline/', views.ApplicationStatusTimelineView.as_view(), name='timeline'),
    path('jobs/<int:pk>/applicants/', views.JobApplicantsListView.as_view(), name='job_applicants'),
]
