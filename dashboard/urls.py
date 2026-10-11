"""URL patterns for dashboard app."""
from django.urls import path
from . import views
from . import admin_views

app_name = 'dashboard'

urlpatterns = [
    # Employee dashboard
    path('', views.EmployeeDashboardView.as_view(), name='employee_dashboard'),
    
    # Admin dashboard
    path('manage/', admin_views.AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # User management
    path('manage/users/', admin_views.UserListView.as_view(), name='user_list'),
    path('manage/users/<int:pk>/', admin_views.UserDetailView.as_view(), name='user_detail'),
    path('manage/users/<int:pk>/toggle-active/', admin_views.UserToggleActiveView.as_view(), name='user_toggle_active'),
    
    # Company management
    path('manage/companies/', admin_views.CompanyManagementListView.as_view(), name='company_management'),
    path('manage/companies/<int:pk>/approve/', admin_views.CompanyApprovalView.as_view(), name='company_approve'),
    path('manage/companies/<int:pk>/reject/', admin_views.CompanyRejectionView.as_view(), name='company_reject'),
    
    # Job management
    path('manage/jobs/', admin_views.JobManagementListView.as_view(), name='job_management'),
    path('manage/jobs/moderation-queue/', admin_views.JobModerationQueueView.as_view(), name='job_moderation_queue'),
    path('manage/jobs/<int:pk>/approve/', admin_views.JobApprovalView.as_view(), name='job_approve'),
    path('manage/jobs/<int:pk>/reject/', admin_views.JobRejectionView.as_view(), name='job_reject'),
    
    # Job reports
    path('manage/reports/', admin_views.JobReportsListView.as_view(), name='job_reports'),
    path('manage/reports/<int:pk>/', admin_views.JobReportDetailView.as_view(), name='job_report_detail'),
    
    # Contact messages
    path('manage/contact/', admin_views.ContactMessagesListView.as_view(), name='contact_messages'),
    path('manage/contact/<int:pk>/', admin_views.ContactMessageDetailView.as_view(), name='contact_message_detail'),
    
    # Audit logs
    path('manage/audit-logs/', admin_views.AuditLogListView.as_view(), name='audit_logs'),
]
