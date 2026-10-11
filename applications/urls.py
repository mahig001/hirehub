"""URL patterns for applications app."""
from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    # Job seeker URLs
    path('jobs/<int:job_pk>/apply/', views.ApplyView.as_view(), name='apply'),
    path('<int:pk>/', views.ApplicationDetailView.as_view(), name='detail'),
    path('<int:pk>/withdraw/', views.WithdrawApplicationView.as_view(), name='withdraw'),
    path('my-applications/', views.MyApplicationsListView.as_view(), name='my_applications'),
    path('<int:pk>/timeline/', views.ApplicationStatusTimelineView.as_view(), name='timeline'),
    
    # Employee/Recruiter URLs
    path('jobs/<int:pk>/applicants/', views.JobApplicantsListView.as_view(), name='job_applicants'),
    path('employee/applications/<int:pk>/', views.ApplicantDetailView.as_view(), name='applicant_detail'),
    path('employee/applications/<int:pk>/schedule-interview/', views.ScheduleInterviewView.as_view(), name='schedule_interview'),
    path('employee/applications/<int:pk>/update-status/', views.UpdateApplicantStatusView.as_view(), name='update_status'),
    path('employee/applications/<int:pk>/add-note/', views.AddApplicantNoteView.as_view(), name='add_note'),
    path('employee/applications/<int:pk>/rate/', views.RateApplicantView.as_view(), name='rate_applicant'),
    path('employee/jobs/<int:job_pk>/applicants/bulk-action/', views.BulkActionView.as_view(), name='bulk_action'),
    path('employee/jobs/<int:job_pk>/applicants/export/', views.ExportApplicantsCSVView.as_view(), name='export_csv'),
]
