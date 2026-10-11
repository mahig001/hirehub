"""Business logic for application management."""
import logging
from datetime import datetime, timedelta
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Application, ApplicationStatusHistory, Interview

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
    
    @staticmethod
    @transaction.atomic
    def schedule_interview(application, interview_data, scheduled_by):
        """
        Schedule an interview for an application.
        
        Args:
            application: Application instance
            interview_data: Dict with interview details
            scheduled_by: User scheduling the interview
            
        Returns:
            Interview instance
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate rating if provided
        rating = interview_data.get('rating')
        if rating is not None and (rating < 1 or rating > 5):
            raise ValidationError('Rating must be between 1 and 5.')
        
        # Create interview
        interview = Interview.objects.create(
            application=application,
            scheduled_at=interview_data['scheduled_at'],
            interview_type=interview_data['interview_type'],
            location=interview_data['location'],
            notes=interview_data.get('notes', ''),
            rating=rating,
            interviewer=interview_data.get('interviewer')
        )
        
        logger.info(f'Interview scheduled: {interview.id} for application {application.id} by {scheduled_by.email}')
        
        # TODO: Send notification signal for interview scheduling
        
        return interview
    
    @staticmethod
    @transaction.atomic
    def add_applicant_note(application, note):
        """
        Add a note to recruiter_notes with timestamp.
        
        Args:
            application: Application instance
            note: Note text to append
            
        Returns:
            Application instance
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_note = f"[{timestamp}] {note}"
        
        if application.recruiter_notes:
            application.recruiter_notes += f"\n\n{new_note}"
        else:
            application.recruiter_notes = new_note
        
        application.save(update_fields=['recruiter_notes', 'updated_at'])
        
        logger.info(f'Note added to application {application.id}')
        
        return application
    
    @staticmethod
    @transaction.atomic
    def rate_applicant(application, rating):
        """
        Set the overall rating for an applicant.
        
        Args:
            application: Application instance
            rating: Integer rating (1-5)
            
        Returns:
            Application instance
            
        Raises:
            ValidationError: If rating is invalid
        """
        if rating < 1 or rating > 5:
            raise ValidationError('Rating must be between 1 and 5.')
        
        application.rating = rating
        application.save(update_fields=['rating', 'updated_at'])
        
        logger.info(f'Application {application.id} rated: {rating}')
        
        return application
    
    @staticmethod
    @transaction.atomic
    def bulk_change_status(application_ids, new_status, changed_by, note=''):
        """
        Change status for multiple applications.
        
        Args:
            application_ids: List of application IDs
            new_status: New status value
            changed_by: User making the change
            note: Optional note about the change
            
        Returns:
            List of updated Application instances
        """
        applications = Application.objects.filter(id__in=application_ids)
        updated = []
        
        for application in applications:
            try:
                ApplicationService.change_status(application, new_status, changed_by, note)
                updated.append(application)
            except ValidationError as e:
                logger.warning(f'Failed to change status for application {application.id}: {e}')
        
        logger.info(f'Bulk status change: {len(updated)} applications updated to {new_status}')
        
        return updated
