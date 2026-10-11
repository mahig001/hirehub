from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('<int:pk>/read/', views.MarkNotificationReadView.as_view(), name='mark_read'),
    path('mark-all-read/', views.MarkAllReadView.as_view(), name='mark_all_read'),
    path('job-alerts/', views.JobAlertListView.as_view(), name='alert_list'),
    path('job-alerts/create/', views.JobAlertCreateView.as_view(), name='alert_create'),
    path('job-alerts/<int:pk>/edit/', views.JobAlertUpdateView.as_view(), name='alert_update'),
    path('job-alerts/<int:pk>/delete/', views.JobAlertDeleteView.as_view(), name='alert_delete'),
    path('job-alerts/<int:pk>/toggle/', views.JobAlertToggleView.as_view(), name='alert_toggle'),
]
