from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Notification model for user notifications."""
    
    APPLICATION_SUBMITTED = 'APPLICATION_SUBMITTED'
    APPLICATION_STATUS_CHANGED = 'APPLICATION_STATUS_CHANGED'
    NEW_APPLICANT = 'NEW_APPLICANT'
    JOB_ALERT = 'JOB_ALERT'
    INTERVIEW_SCHEDULED = 'INTERVIEW_SCHEDULED'
    
    NOTIFICATION_TYPE_CHOICES = [
        (APPLICATION_SUBMITTED, 'Application Submitted'),
        (APPLICATION_STATUS_CHANGED, 'Application Status Changed'),
        (NEW_APPLICANT, 'New Applicant'),
        (JOB_ALERT, 'Job Alert'),
        (INTERVIEW_SCHEDULED, 'Interview Scheduled'),
    ]
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.recipient} - {self.title}'


class JobAlert(models.Model):
    """Job alert model for email notifications of matching jobs."""
    
    DAILY = 'DAILY'
    WEEKLY = 'WEEKLY'
    
    FREQUENCY_CHOICES = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_alerts'
    )
    category = models.ForeignKey(
        'jobs.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    keywords = models.CharField(
        max_length=500,
        blank=True,
        help_text='Comma-separated search terms'
    )
    location = models.CharField(max_length=200, blank=True)
    job_type = models.CharField(max_length=50, blank=True)
    frequency = models.CharField(
        max_length=10,
        choices=FREQUENCY_CHOICES,
        default=DAILY
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f'Job Alert for {self.user.get_full_name()}'
