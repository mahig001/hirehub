from django.db import models
from django.conf import settings
from jobs.models import Job


class Application(models.Model):
    """Job application model."""
    
    PENDING = 'PENDING'
    REVIEWING = 'REVIEWING'
    SHORTLISTED = 'SHORTLISTED'
    REJECTED = 'REJECTED'
    WITHDRAWN = 'WITHDRAWN'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (REVIEWING, 'Reviewing'),
        (SHORTLISTED, 'Shortlisted'),
        (REJECTED, 'Rejected'),
        (WITHDRAWN, 'Withdrawn'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['job', 'applicant']]
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['job', 'status']),
            models.Index(fields=['applicant', 'status']),
            models.Index(fields=['-applied_at']),
        ]
    
    def __str__(self):
        return f'{self.applicant.get_full_name()} - {self.job.title}'


class ApplicationStatusHistory(models.Model):
    """Audit trail for application status changes."""
    
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='application_status_changes'
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['application', '-changed_at']),
        ]
        verbose_name_plural = 'Application status histories'
    
    def __str__(self):
        return f'{self.application} - {self.old_status} → {self.new_status}'
