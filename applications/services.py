"""Business logic for application management."""
import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Application, ApplicationStatusHistory

logger = logging.getLogger(__name__)

User = get_user_model()


class ApplicationService:
    """Service for managing job applications."""
    
    @staticmethod
    @transaction.atomic
    def create_application(job, applicant, cover_letter=''):
        """
        Create a new job application.
        
        Args:
            job: Job instance
            applicant: User instance (job seeker)
            cover_letter: Optional cover letter text
            
        Returns:
            Application instance
            
        Raises:
            ValidationError: If application already exists or validation fails
        """
        # Check if application already exists
        if Application.objects.filter(job=job, applicant=applicant).exists():
            raise ValidationError('You have already applied to this job.')
        
        # Create application
        application = Application.objects.create(
            job=job,
            applicant=applicant,
            cover_letter=cover_letter,
            status=Application.PENDING
        )
        
        # Create initial status history
        ApplicationStatusHistory.objects.create(
            application=application,
            old_status='',
            new_status=Application.PENDING,
            changed_by=applicant,
            note='Application submitted'
        )
        
        logger.info(f'Application created: {application.id} by {applicant.email} for job {job.id}')
        
        # TODO: Send notification to applicant (confirmation)
        # TODO: Send notification to company/recruiter (new application)
        
        return application
    
    @staticmethod
    @transaction.atomic
    def change_status(application, new_status, changed_by, note=''):
        """
        Change application status and create history record.
        
        Args:
            application: Application instance
            new_status: New status value
            changed_by: User making the change
            note: Optional note about the change
            
        Returns:
            Application instance
            
        Raises:
            ValidationError: If status transition is invalid
        """
        # Validate status
        valid_statuses = [choice[0] for choice in Application.STATUS_CHOICES]
        if new_status not in valid_statuses:
            raise ValidationError(f'Invalid status: {new_status}')
        
        old_status = application.status
        
        # Don't create history if status hasn't changed
        if old_status == new_status:
            return application
        
        # Update application status
        application.status = new_status
        application.save(update_fields=['status', 'updated_at'])
        
        # Create status history
        ApplicationStatusHistory.objects.create(
            application=application,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            note=note
        )
        
        logger.info(f'Application {application.id} status changed from {old_status} to {new_status} by {changed_by.email}')
        
        # TODO: Send notification to applicant about status change
        
        return application
    
    @staticmethod
    @transaction.atomic
    def withdraw_application(application, user):
        """
        Withdraw an application (set status to WITHDRAWN).
        
        Args:
            application: Application instance
            user: User withdrawing the application (must be applicant)
            
        Returns:
            Application instance
            
        Raises:
            ValidationError: If user is not the applicant or status is already withdrawn
        """
        # Verify user is the applicant
        if application.applicant != user:
            raise ValidationError('You can only withdraw your own applications.')
        
        # Check if already withdrawn
        if application.status == Application.WITHDRAWN:
            raise ValidationError('This application has already been withdrawn.')
        
        # Change status to WITHDRAWN
        return ApplicationService.change_status(
            application,
            Application.WITHDRAWN,
            user,
            'Application withdrawn by applicant'
        )
    
    @staticmethod
    def get_status_history(application):
        """
        Get status history for an application.
        
        Args:
            application: Application instance
            
        Returns:
            QuerySet of ApplicationStatusHistory
        """
        return application.status_history.select_related('changed_by').all()
