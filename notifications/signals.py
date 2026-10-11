import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from applications.models import Application, Interview
from .services import NotificationService
from .models import Notification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Application)
def on_application_created(sender, instance, created, **kwargs):
    """
    Signal handler for when an application is created.
    Sends notification to company employees/owner about new applicant.
    """
    if not created:
        return
    
    try:
        # Get company employees
        company = instance.job.company
        from companies.models import Employee
        employees = Employee.objects.filter(company=company).select_related('user')
        
        # Create notification and send email to each employee
        for employee in employees:
            # Create notification
            NotificationService.create_notification(
                recipient=employee.user,
                notification_type=Notification.NEW_APPLICANT,
                title=f'New Application: {instance.job.title}',
                message=f'{instance.applicant.get_full_name()} has applied for {instance.job.title}',
                link=reverse('applications:detail', kwargs={'pk': instance.pk})
            )
            
            # Send email
            NotificationService.send_email_notification(
                recipient=employee.user,
                subject=f'New Application for {instance.job.title}',
                template_name='notifications/emails/application_submitted_email.html',
                context={
                    'applicant_name': instance.applicant.get_full_name(),
                    'job_title': instance.job.title,
                    'company_name': company.name,
                    'application_link': reverse('applications:detail', kwargs={'pk': instance.pk}),
                }
            )
        
        logger.info(f'Sent new applicant notifications for application {instance.id}')
    except Exception as e:
        logger.error(f'Error in on_application_created signal: {e}')


# Track previous status for status change detection
_application_status_tracker = {}


@receiver(pre_save, sender=Application)
def track_application_status(sender, instance, **kwargs):
    """Track the old status before save."""
    if instance.pk:
        try:
            old_instance = Application.objects.get(pk=instance.pk)
            _application_status_tracker[instance.pk] = old_instance.status
        except Application.DoesNotExist:
            pass


@receiver(post_save, sender=Application)
def on_application_status_changed(sender, instance, created, **kwargs):
    """
    Signal handler for when an application status changes.
    Sends notification to applicant about status change.
    """
    if created:
        return
    
    try:
        # Check if status changed
        old_status = _application_status_tracker.get(instance.pk)
        if old_status and old_status != instance.status:
            # Create notification
            NotificationService.create_notification(
                recipient=instance.applicant,
                notification_type=Notification.APPLICATION_STATUS_CHANGED,
                title=f'Application Status Updated: {instance.job.title}',
                message=f'Your application status has been changed to {instance.get_status_display()}',
                link=reverse('applications:detail', kwargs={'pk': instance.pk})
            )
            
            # Send email
            NotificationService.send_email_notification(
                recipient=instance.applicant,
                subject=f'Application Status Update: {instance.job.title}',
                template_name='notifications/emails/application_status_changed_email.html',
                context={
                    'job_title': instance.job.title,
                    'new_status': instance.get_status_display(),
                    'application_link': reverse('applications:detail', kwargs={'pk': instance.pk}),
                }
            )
            
            # Clean up tracker
            if instance.pk in _application_status_tracker:
                del _application_status_tracker[instance.pk]
            
            logger.info(f'Sent status change notification for application {instance.id}')
    except Exception as e:
        logger.error(f'Error in on_application_status_changed signal: {e}')


@receiver(post_save, sender=Interview)
def on_interview_scheduled(sender, instance, created, **kwargs):
    """
    Signal handler for when an interview is scheduled.
    Sends notification to applicant with interview details.
    """
    if not created:
        return
    
    try:
        # Create notification
        NotificationService.create_notification(
            recipient=instance.application.applicant,
            notification_type=Notification.INTERVIEW_SCHEDULED,
            title=f'Interview Scheduled: {instance.application.job.title}',
            message=f'An interview has been scheduled for {instance.scheduled_at.strftime("%B %d, %Y at %I:%M %p")}',
            link=reverse('applications:detail', kwargs={'pk': instance.application.pk})
        )
        
        # Send email
        NotificationService.send_email_notification(
            recipient=instance.application.applicant,
            subject=f'Interview Scheduled: {instance.application.job.title}',
            template_name='notifications/emails/interview_scheduled_email.html',
            context={
                'job_title': instance.application.job.title,
                'interview_type': instance.get_interview_type_display(),
                'scheduled_at': instance.scheduled_at,
                'location': instance.location,
                'notes': instance.notes,
                'application_link': reverse('applications:detail', kwargs={'pk': instance.application.pk}),
            }
        )
        
        logger.info(f'Sent interview scheduled notification for interview {instance.id}')
    except Exception as e:
        logger.error(f'Error in on_interview_scheduled signal: {e}')
