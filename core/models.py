from django.db import models
from django.conf import settings


class ContactMessage(models.Model):
    """Contact form submission model."""
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_read']),
        ]
    
    def __str__(self):
        return f'{self.subject} from {self.name}'


class AuditLog(models.Model):
    """Audit log for tracking admin actions."""
    
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=100)
    target_model = models.CharField(max_length=100)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['actor']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        actor_name = self.actor.get_full_name() if self.actor else 'System'
        return f'{actor_name}: {self.action} on {self.target_model}'
